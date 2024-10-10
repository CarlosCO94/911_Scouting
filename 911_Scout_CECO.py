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

# Título de la aplicación
st.title("Comparación de Jugadores")

# URLs directas de los archivos CSV (reemplaza con las URLs correctas)
data_url = 'https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/nombre_del_archivo.csv'
logo_url = 'https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Wyscout_Logo_URL.csv'

# Función para cargar datos CSV desde una URL
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Cargar los datos principales y los logos
data = cargar_datos_csv(data_url)
logos = cargar_datos_csv(logo_url)

# Verificar si los datos se cargaron correctamente
if data.empty or logos.empty:
    st.error("No se pudieron cargar los datos desde las URLs proporcionadas.")
else:
    # Mostrar las columnas disponibles en el DataFrame para depurar
    st.write("Columnas disponibles en el DataFrame:", data.columns.tolist())

    # Filtrado de temporadas
    available_seasons = sorted(data['Season'].unique())
    selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", available_seasons)

    if selected_seasons:
        filtered_data = data[data['Season'].isin(selected_seasons)]

        if filtered_data.empty:
            st.error(f"No se encontraron datos para las temporadas seleccionadas: {', '.join(selected_seasons)}.")
        else:
            equipos_disponibles = filtered_data['Team'].unique()
            equipos_disponibles = ['Todos'] + sorted(equipos_disponibles)

            equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", equipos_disponibles)

            if equipo_seleccionado == 'Todos':
                jugadores_filtrados_por_equipo = filtered_data
            else:
                jugadores_filtrados_por_equipo = filtered_data[filtered_data['Team'] == equipo_seleccionado]

            jugadores_comparacion = st.sidebar.multiselect(
                "Selecciona los jugadores para comparar (el primero será el jugador principal):", 
                jugadores_filtrados_por_equipo['Full name'].unique()
            )

            if jugadores_comparacion:
                jugador_principal = jugadores_comparacion[0]

                posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion]

                # Crear una tabla con las métricas de comparación de los jugadores
                jugadores_filtrados = filtered_data[filtered_data['Full name'].isin(jugadores_comparacion)]
                jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()

                # Mostrar la tabla de comparación
                st.write(f"Comparación de jugadores para la posición: {posicion}")
                st.dataframe(jugadores_comparativos)
