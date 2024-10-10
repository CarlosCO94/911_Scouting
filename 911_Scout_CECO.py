import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# URL de la API de GitHub para obtener el contenido de la carpeta "Main APP"
url_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Función para cargar datos CSV con caché
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Obtener la lista de archivos CSV en la carpeta "Main APP" del repositorio
file_urls = []
try:
    response = requests.get(url_base)
    if response.status_code == 200:
        archivos = response.json()
        # Generar la URL de descarga directa para cada archivo CSV encontrado
        file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Verificar que se encontraron archivos CSV
if not file_urls:
    st.error("No se encontraron archivos CSV en la carpeta Main APP.")
else:
    data_frames = []
    for url in file_urls:
        df = cargar_datos_csv(url)
        if not df.empty:
            data_frames.append(df)

    # Combinar los dataframes si hay más de uno
    if data_frames:
        combined_data = pd.concat(data_frames, ignore_index=True)
        st.write("Datos combinados:", combined_data)
    else:
        st.error("No se encontraron datos en los archivos CSV proporcionados.")

# Título de la aplicación
st.title("Comparación de Jugadores")

# Diccionario de métricas por posición corregido y actualizado según las métricas disponibles en el CSV
metricas_por_posicion = {
    'Portero': ["Minutes played", "Conceded goals per 90", "Shots against per 90", "Clean sheets", "Save rate, %", 
                "xG against per 90", "Prevented goals per 90", "Back passes received as GK per 90", 
                "Exits per 90", "Aerial duels per 90"],
    'Centrales': ["Minutes played", "Defensive actions per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Sliding tackles per 90", "Possession won after a tackle", "Shots blocked per 90", 
                  "Interceptions per 90", "Forward passes per 90", "Through passes per 90", "Head goals"],
    'Laterales': ["Minutes played", "Assists per 90", "Duels per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Shots blocked per 90", "Interceptions per 90", "Goals per 90", "Shots per 90", 
                  "Crosses per 90", "Dribbles per 90", "Offensive duels per 90", "Forward passes per 90"],
    'Volantes Centrales + MCO': ["Minutes played", "Goals", "Assists per 90", "Duels won, %", "Successful defensive actions per 90", 
                                 "Defensive duels per 90", "Long passes per 90", "Aerial duels per 90", 
                                 "Interceptions per 90", "Forward passes per 90", "Through passes per 90"],
    'Delantero + Extremos': ["Minutes played", "Goals per 90", "Assists per 90", "Shots per 90", "Shots on target, %", 
                             "Successful dribbles per 90", "Offensive duels per 90", "Received passes per 90", 
                             "Crosses per 90", "Dribbles per 90", "Accurate passes, %", "Forward passes per 90", 
                             "Through passes per 90"]
}

# Verificar que los datos se hayan cargado correctamente
if 'combined_data' in locals() and not combined_data.empty:
    st.sidebar.header("Opciones de Comparación de Jugadores")
    
    # Selección de temporadas y filtrado de datos
    available_seasons = sorted(combined_data['Season'].unique())
    selected_seasons = st.sidebar.multiselect("Selecciona la(s) temporada(s):", available_seasons)
    
    filtered_data = combined_data[combined_data['Season'].isin(selected_seasons)] if selected_seasons else combined_data
    
    if not filtered_data.empty:
        equipos_disponibles = ['Todos'] + sorted(filtered_data['Team within selected timeframe'].unique())
        equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", equipos_disponibles)
        
        if equipo_seleccionado != 'Todos':
            jugadores_filtrados_por_equipo = filtered_data[filtered_data['Team within selected timeframe'] == equipo_seleccionado]
        else:
            jugadores_filtrados_por_equipo = filtered_data
        
        jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar:", jugadores_filtrados_por_equipo['Full name'].unique())

        if jugadores_comparacion:
            posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
            metricas_filtradas = metricas_por_posicion[posicion]
            
            jugadores_filtrados = jugadores_filtrados_por_equipo[jugadores_filtrados_por_equipo['Full name'].isin(jugadores_comparacion)]
            
            jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()
            
            st.write("Comparación de Jugadores:")
            st.dataframe(jugadores_comparativos)
    else:
        st.error("No se encontraron datos para las temporadas seleccionadas.")

