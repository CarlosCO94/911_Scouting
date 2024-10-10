import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re  # Para usar expresiones regulares

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición
metricas_por_posicion = {
    'Portero': ["Minutes played", "Conceded goals per 90", "Shots against per 90", "Clean sheets", "Save rate, %", 
                "xG against per 90", "Prevented goals per 90", "Back passes received as GK per 90", 
                "Exits per 90", "Aerial duels per 90"],
    'Centrales': ["Minutes played", "Successful defensive actions per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Sliding tackles per 90", "Shots blocked per 90", "Interceptions per 90", 
                  "Forward passes per 90", "Through passes per 90", "Head goals"],
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

# URL base de la API de GitHub para listar los archivos en la carpeta "Main APP"
url_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Función para cargar datos CSV desde una URL con caché
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Función para obtener la lista de archivos CSV en la carpeta "Main APP"
def obtener_lista_archivos_csv(url_base):
    response = requests.get(url_base)
    if response.status_code == 200:
        archivos = response.json()
        return [(file['download_url'], re.search(r'(\d{4})', file['name']).group(1)) for file in archivos if file['name'].endswith('.csv') and re.search(r'(\d{4})', file['name'])]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
        return []

# Obtener la lista de URLs de todos los archivos CSV en la carpeta "Main APP" junto con la temporada extraída
csv_urls_with_seasons = obtener_lista_archivos_csv(url_base)

# Verificar que se encontraron archivos CSV
if not csv_urls_with_seasons:
    st.error("No se encontraron archivos CSV en la carpeta Main APP.")
else:
    # Cargar y combinar todos los archivos CSV en un solo DataFrame
    data_frames = []
    for url, season in csv_urls_with_seasons:
        df = cargar_datos_csv(url)
        if not df.empty:
            df['Season'] = season  # Añadir la temporada como una nueva columna
            data_frames.append(df)

    if data_frames:
        data = pd.concat(data_frames, ignore_index=True)
    else:
        data = pd.DataFrame()  # Si no se pudieron cargar los datos, crear un DataFrame vacío

    # Verificar si el DataFrame combinado está vacío
    if data.empty:
        st.error("No se pudieron cargar los datos desde las URLs proporcionadas.")
    else:
        # Mostrar todas las columnas disponibles en el DataFrame para depurar
        st.write("Columnas disponibles en el DataFrame:", data.columns.tolist())

        # Filtrado de temporadas utilizando la columna 'Season'
        available_seasons = sorted(data['Season'].unique())
        selected_season = st.sidebar.selectbox("Selecciona el año o temporada", available_seasons)

        if selected_season:
            filtered_data = data[data['Season'] == selected_season]

            if filtered_data.empty:
                st.error(f"No se encontraron datos para la temporada seleccionada: {selected_season}.")
            else:
                jugadores_seleccionados = st.sidebar.multiselect(
                    "Selecciona uno o más jugadores para comparar:", 
                    filtered_data['Full name'].unique()
                )

                if jugadores_seleccionados:
                    posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                    metricas_filtradas = st.sidebar.multiselect(
                        "Selecciona una o más métricas para mostrar:", 
                        metricas_por_posicion[posicion]
                    )

                    if metricas_filtradas:
                        # Crear una tabla con las métricas de comparación de los jugadores seleccionados
                        jugadores_filtrados = filtered_data[filtered_data['Full name'].isin(jugadores_seleccionados)]
                        jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()

                        # Mostrar la tabla de comparación
                        st.write(f"Comparación de jugadores para la posición: {posicion}")
                        st.dataframe(jugadores_comparativos)
                    else:
                        st.warning("Por favor, selecciona al menos una métrica para mostrar.")
        else:
            st.error("Por favor, selecciona una temporada.")
