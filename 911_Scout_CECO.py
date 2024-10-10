import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

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

# URL del CSV de logos de equipos
url_logos = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Wyscout_Logo_URL.csv"

# Función para cargar datos CSV desde una URL
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Cargar los logos de los equipos
logos_df = cargar_datos_csv(url_logos)

# URL de la carpeta "Main APP" en GitHub
url_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Obtener la lista de archivos CSV en la carpeta "Main APP"
response = requests.get(url_base)
file_urls = []
if response.status_code == 200:
    archivos = response.json()
    file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
else:
    st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")

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

# Verificar que hay temporadas disponibles
if not available_seasons:
    st.error("No se encontraron temporadas en los archivos CSV.")
else:
    selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", sorted(available_seasons))

    if selected_seasons:
        filtered_data = pd.concat(
            [data_by_season[filename] for filename in data_by_season if any(season in filename for season in selected_seasons)],
            ignore_index=True
        )

        if filtered_data.empty:
            st.error(f"No se encontraron datos para las temporadas seleccionadas: {', '.join(selected_seasons)}.")
        else:
            equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", filtered_data['Team within selected timeframe'].unique())
            jugadores_filtrados = filtered_data[filtered_data['Team within selected timeframe'] == equipo_seleccionado]

            jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar", jugadores_filtrados['Full name'].unique())

            if jugadores_comparacion:
                posicion = st.sidebar.selectbox("Selecciona la posición del jugador", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion]

                # Mostrar la comparación de jugadores con métricas originales
                st.write(f"Comparación de jugadores para la posición: {posicion}")
                jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()

                # Añadir logo del equipo al lado de los nombres de los jugadores
                for jugador in jugadores_comparacion:
                    equipo = jugadores_filtrados[jugadores_filtrados['Full name'] == jugador]['Team within selected timeframe'].values[0]
                    logo_url = logos_df[logos_df['Equipo'] == equipo]['Logo URL'].values[0]
                    st.image(logo_url, width=50, caption=equipo)

                st.dataframe(jugadores_comparativos)

        # Mostrar la comparación de jugadores con métricas traducidas
        st.write(f"Comparación de jugadores para la posición: {posicion}")
        jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()
        st.dataframe(jugadores_comparativos)
