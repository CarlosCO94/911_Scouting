import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
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
        file_names = [file['name'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Verificar que se encontraron archivos CSV
if not file_urls:
    st.error("No se encontraron archivos CSV en la carpeta Main APP.")
else:
    data_frames = []
    for url, name in zip(file_urls, file_names):
        df = cargar_datos_csv(url)
        if not df.empty:
            # Extraer la temporada del nombre del archivo usando expresiones regulares
            match = re.search(r'(\d{4}(?:-\d{2,4})?)', name)
            if match:
                season = match.group(1)
                df['Season'] = season  # Añadir la columna 'Season' al DataFrame
            else:
                df['Season'] = 'Desconocida'  # Asignar 'Desconocida' si no se encuentra la temporada
            data_frames.append(df)

    # Combinar los dataframes si hay más de uno
    if data_frames:
        combined_data = pd.concat(data_frames, ignore_index=True)
        st.write("Datos combinados:", combined_data)
        
        # Mostrar las columnas disponibles para depurar
        st.write("Columnas disponibles en el DataFrame combinado:", combined_data.columns.tolist())

        # Verificar si la columna 'Season' existe antes de continuar
        if 'Season' in combined_data.columns:
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
        else:
            st.error("La columna 'Season' no está presente en los datos combinados.")
    else:
        st.error("No se encontraron datos en los archivos CSV proporcionados.")


