import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición
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

# URL del archivo CSV que contiene la información de las ligas
league_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Ligas_Wyscout.csv"

# URL base para acceder a los archivos directamente en GitHub
base_raw_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"
api_url = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Función para cargar archivos CSV con caché
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Cargar la información de las ligas
league_data = cargar_datos_csv(league_url)

# Obtener la lista de archivos CSV en la carpeta "Main APP" del repositorio
file_urls = []
try:
    response = requests.get(api_url)
    if response.status_code == 200:
        archivos = response.json()
        file_urls = [base_raw_url + file['name'] for file in archivos if file['name'].endswith('.csv')]
        file_names = [file['name'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Cargar datos de los jugadores
data_frames = []
if file_urls:
    for url, name in zip(file_urls, file_names):
        df = cargar_datos_csv(url)
        if not df.empty:
            match = re.search(r'(\d{4}(?:-\d{2,4})?)', name)
            if match:
                season = match.group(1)
                df['Season'] = season
            else:
                df['Season'] = 'Desconocida'
            data_frames.append(df)

# Combinar todos los dataframes si hay más de uno
if data_frames:
    combined_data = pd.concat(data_frames, ignore_index=True)

# Verificar si las columnas 'Full name' y 'Team logo' existen antes de continuar
required_columns = ['Full name', 'Team logo']
missing_columns = [col for col in required_columns if col not in combined_data.columns]
if missing_columns:
    st.error(f"Las siguientes columnas necesarias no están presentes en los datos: {', '.join(missing_columns)}")
else:
    # Crear pestañas para organizar la interfaz de la aplicación
    tabs = st.tabs(["Player Search and Results", "Player Radar Generation", "Scatter Plots"])

    # Primera pestaña: Player Search and Results
    with tabs[0]:
        st.header("Player Search and Results")

        # Multiselect para seleccionar temporadas
        available_seasons = sorted(combined_data['Season'].unique())
        selected_seasons = st.multiselect("Selecciona las temporadas:", available_seasons)

        # Filtrar los datos para las temporadas seleccionadas
        filtered_data = combined_data[combined_data['Season'].isin(selected_seasons)]

        # Multiselect para seleccionar jugadores
        jugadores_disponibles = sorted(filtered_data['Full name'].unique())
        jugadores_seleccionados = st.multiselect("Selecciona los jugadores:", jugadores_disponibles)

        # Select box para seleccionar la posición del jugador y mostrar las métricas correspondientes
        posicion_seleccionada = st.selectbox("Selecciona la posición del jugador:", metricas_por_posicion.keys())
        metricas_filtradas = metricas_por_posicion[posicion_seleccionada]

        # Multiselect para seleccionar métricas adicionales
        todas_las_metricas = sorted([col for col in combined_data.columns if col not in ['Full name', 'Season', 'Team logo']])
        metricas_adicionales = st.multiselect("Selecciona métricas adicionales:", todas_las_metricas)

        # Unir las métricas por posición y las métricas adicionales seleccionadas
        metricas_finales = [metrica for metrica in metricas_filtradas + metricas_adicionales if metrica in filtered_data.columns]

        # Mostrar los datos de los jugadores seleccionados con las métricas correspondientes y el logo del equipo
        if jugadores_seleccionados:
            jugadores_data = filtered_data[filtered_data['Full name'].isin(jugadores_seleccionados)][['Full name', 'Team logo'] + metricas_finales]
            st.markdown(jugadores_data.to_html(escape=False, index=False), unsafe_allow_html=True)
    # Segunda pestaña: Player Radar Generation
    with tabs[1]:
        st.header("Player Radar Generation")
    
        # Verificar si el archivo de ligas tiene la columna necesaria
        if 'League' not in league_data.columns:
            st.error("La columna 'League' no se encontró en el archivo Ligas_Wyscout.csv.")
        else:
            # Select box para seleccionar la liga basado en el archivo de ligas cargado
            selected_league = st.selectbox("Selecciona la liga:", sorted(league_data['League'].unique()))
    
            # Filtrar equipos según la liga seleccionada en los datos combinados de jugadores
            filtered_teams = combined_data[combined_data['League'] == selected_league]['Team'].unique()
            selected_team = st.selectbox("Selecciona el equipo:", sorted(filtered_teams))
    
            # Filtro de edad
            age_range = st.slider("Selecciona el rango de edad:", int(combined_data['Age'].min()), int(combined_data['Age'].max()), (18, 35))
    
            # Filtro de pierna preferida
            selected_foot = st.selectbox("Selecciona el pie preferido:", sorted(combined_data['Foot'].unique()))
    
            # Filtrar los jugadores según los criterios seleccionados
            jugadores_filtrados = combined_data[
                (combined_data['League'] == selected_league) &
                (combined_data['Team'] == selected_team) &
                (combined_data['Age'].between(age_range[0], age_range[1])) &
                (combined_data['Foot'] == selected_foot)
            ]['Full name'].unique()
    
            # Select box para elegir un jugador específico
            selected_player = st.selectbox("Selecciona el jugador:", sorted(jugadores_filtrados))
    
            # Mostrar los detalles del jugador seleccionado si hay un jugador elegido
            if selected_player:
                st.write(f"Mostrando datos para el jugador: {selected_player}")
