import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# URLs de los CSV para traducciones y logos
metricas_traducidas_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Traducción_Metricas.csv"
logos_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Wyscout_Logo_URL.csv"

# Función para cargar CSV con manejo de errores
def cargar_csv(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Cargar las métricas traducidas y los logos
metricas_traducidas_df = cargar_csv(metricas_traducidas_url)
logos_df = cargar_csv(logos_url)

# Crear diccionario de traducciones de métricas si las columnas son correctas
if 'Métrica Original' in metricas_traducidas_df.columns and 'Métrica Traducida' in metricas_traducidas_df.columns:
    diccionario_traducciones = dict(zip(metricas_traducidas_df['Métrica Original'], metricas_traducidas_df['Métrica Traducida']))
else:
    st.error("No se encontraron las columnas esperadas en el archivo de métricas traducidas.")

# Diccionario de métricas por posición
metricas_por_posicion = {
    'Portero': ["Minutes played", "Conceded goals per 90", "Shots against per 90", "Clean sheets", "Save rate, %", 
                "xG against per 90", "Prevented goals per 90", "Back passes received as GK per 90", 
                "Exits per 90", "Aerial duels per 90"],
    'Centrales': ["Minutes played", "Successful defensive actions per 90", "Defensive duels per 90", 
                  "Aerial duels per 90", "Sliding tackles per 90", "Interceptions per 90", "Forward passes per 90"],
    'Laterales': ["Minutes played", "Assists per 90", "Duels per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Shots blocked per 90", "Interceptions per 90", "Goals per 90", "Crosses per 90", "Dribbles per 90"],
    'Volantes Centrales + MCO': ["Minutes played", "Goals", "Assists per 90", "Duels won, %", "Defensive duels per 90", 
                                 "Interceptions per 90", "Forward passes per 90", "Through passes per 90"],
    'Delantero + Extremos': ["Minutes played", "Goals per 90", "Assists per 90", "Shots per 90", "Shots on target, %", 
                             "Successful dribbles per 90", "Offensive duels per 90", "Received passes per 90"]
}

# URL de la carpeta "Main APP" en GitHub para cargar datos de jugadores
url_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Función para cargar datos CSV de la API de GitHub
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Obtener la lista de archivos CSV de la API de GitHub
response = requests.get(url_base)
if response.status_code == 200:
    archivos = response.json()
    file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
else:
    st.error("Error al acceder a la carpeta Main APP.")

# Cargar datos y organizar por temporadas
data_by_season = {}
available_seasons = set()

for url in file_urls:
    data = cargar_datos_csv(url)
    if not data.empty:
        season_match = re.findall(r'(\d{4}|\d{2}-\d{2})', url)
        if season_match:
            available_seasons.update(season_match)
            data_by_season[url] = data

# Selección de temporadas y visualización
selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", sorted(available_seasons))
if selected_seasons:
    filtered_data = pd.concat(
        [data_by_season[filename] for filename in data_by_season if any(season in filename for season in selected_seasons)],
        ignore_index=True
    )

    # Mostrar jugadores y sus métricas según la posición
    equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", filtered_data['Team within selected timeframe'].unique())
    jugadores_filtrados = filtered_data[filtered_data['Team within selected timeframe'] == equipo_seleccionado]

    jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar", jugadores_filtrados['Full name'].unique())

    if jugadores_comparacion:
        posicion = st.sidebar.selectbox("Selecciona la posición del jugador", metricas_por_posicion.keys())
        metricas_filtradas = metricas_por_posicion[posicion]

        # Traducir las métricas a mostrar
        metricas_mostrar = [diccionario_traducciones.get(metrica, metrica) for metrica in metricas_filtradas]

        # Mostrar la comparación de jugadores con métricas traducidas
        st.write(f"Comparación de jugadores para la posición: {posicion}")
        jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()
        st.dataframe(jugadores_comparativos)
