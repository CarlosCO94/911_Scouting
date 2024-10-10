import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición corregido y revisado para asegurarse de que las llaves estén bien cerradas
metricas_por_posicion = {
    'Portero': ["Matches played", "Minutes played", "Conceded goals per 90", "xG against per 90", "Prevented goals per 90", "Save rate, %", 
                "Exits per 90", "Aerial duels per 90", "Back passes received as GK per 90", 
                "Accurate passes, %", "Accurate forward passes, %", "Accurate long passes, %"],
    'Centrales': ["Minutes played", "Defensive actions per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Sliding tackles per 90", "Possession won after a tackle", "Shots blocked per 90", 
                  "Possession won after an interception", "Forward passes per 90", "Through passes per 90", 
                  "Head goals"],
    'Laterales': ["Minutes played", "Assists per 90", "Duels per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Shots blocked per 90", "Interceptions per 90", "Goals per 90", "Shots per 90", 
                  "Crosses per 90", "Dribbles per 90", "Offensive duels per 90", "Forward passes per 90"],
    'Volantes Centrales + MCO': ["Minutes played", "Goals", "Assists per 90", "Duels won, %", "Defensive actions per 90", 
                                 "Defensive duels per 90", "Long passes per 90", "Aerial duels per 90", 
                                 "Interceptions per 90", "Forward passes per 90", "Through passes per 90"],
    'Delantero + Extremos': ["Minutes played", "Assists per 90", "Duels per 90", "Successful attacking actions per 90",
                             "Goals per 90", "Head goals per 90", "Shots per 90", "Shots on target, %",
                             "Successful dribbles per 90", "Offensive duels per 90", "Received passes per 90", 
                             "Accurate passes, %", "Forward passes per 90", "Accurate through passes per 90", 
                             "Dribbles per 90"]
}

# Título de la aplicación
st.title("Comparación de Jugadores")

# URL de la carpeta "Main APP" en GitHub
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

# Inicializar file_urls
file_urls = []

# Obtener la lista de archivos CSV en la carpeta "Main APP"
try:
    response = requests.get(url_base)
    if response.status_code == 200:
        archivos = response.json()
        file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Verificar que file_urls esté definido antes de su uso
if not file_urls:
    st.error("No se encontraron archivos CSV en la carpeta Main APP.")

data_by_season = {}
available_seasons = set()

for url in file_urls:
    data = cargar_datos_csv(url)
    if not data.empty:
        matches = re.findall(r'(\d{4}|\d{2}-\d{2})', url.split('/')[-1])
        if matches:
            for match in matches:
                if any(match in filename for filename in data_by_season):  # Verificar si la temporada existe en los archivos
                    available_seasons.add(match)
        data_by_season[url.split('/')[-1]] = data

# Verificar que hay temporadas disponibles
if not available_seasons:
    st.error("No se encontraron temporadas en los archivos CSV.")
else:
    # Cambiar el selectbox para la selección de temporadas a un multiselect
    selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", sorted(available_seasons))
    
    # Filtrar los datos para las temporadas seleccionadas
    if selected_seasons:
        filtered_data = pd.concat(
            [data for filename, data in data_by_season.items() if any(season in filename for season in selected_seasons)],
            ignore_index=True
        )
    
        if filtered_data.empty:
            st.error(f"No se encontraron datos para las temporadas seleccionadas: {', '.join(selected_seasons)}.")
        else:
            if 'Full name' in filtered_data.columns and 'Team logo' in filtered_data.columns and 'Team within selected timeframe' in filtered_data.columns:
                equipos_disponibles = filtered_data['Team within selected timeframe'].unique()
                equipos_disponibles = [str(equipo) for equipo in equipos_disponibles]
                equipos_disponibles = ['Todos'] + sorted(equipos_disponibles)
    
                equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", equipos_disponibles)
    
                if equipo_seleccionado == 'Todos':
                    jugadores_filtrados_por_equipo = filtered_data
                else:
                    jugadores_filtrados_por_equipo = filtered_data[filtered_data['Team within selected timeframe'] == equipo_seleccionado]
    
                jugadores_comparacion = st.sidebar.multiselect(
                    "Selecciona los jugadores para comparar (el primero será el jugador principal):", 
                    jugadores_filtrados_por_equipo['Full name'].unique()
                )
    
                if jugadores_comparacion:
                    jugador_principal = jugadores_comparacion[0]
    
                    posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                    metricas_filtradas = metricas_por_posicion[posicion]
    
                    # Nuevo multiselect para seleccionar las métricas específicas del CSV
                    todas_las_metricas = filtered_data.columns.tolist()
                    metricas_seleccionadas = st.sidebar.multiselect("Selecciona las métricas a mostrar:", todas_las_metricas)
    
                    jugadores_filtrados = filtered_data[filtered_data['Full name'].isin(jugadores_comparacion)]
    
                    # Crear una tabla con los logos de los equipos y los nombres de los jugadores
                    logos_html = jugadores_filtrados[['Full name', 'Team logo']].drop_duplicates().set_index('Full name').T
                    logos_html = logos_html.applymap(lambda url: f'<div style="text-align: center;"><img src="{url}" width="50"></div>')

                    # Crear una tabla con las métricas de comparación de los jugadores
                    metricas_combinar = metricas_filtradas + metricas_seleccionadas  # Mantener todas las métricas seleccionadas en la tabla
                    jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_combinar].transpose()
    
                    # Alinear la tabla de logos con la tabla de métricas para una mejor presentación
                    logos_html.columns = jugadores_comparativos.columns
    
                    # Aplicar formato para resaltar los valores máximos de cada métrica
                    jugadores_comparativos_html = jugadores_comparativos.apply(
                        lambda row: row.apply(
                            lambda x: f'<div style="text-align: center; background-color: yellow; color: black;">{x}</div>' if x == row.max() else f'<div style="text-align: center;">{x}</div>'
                        ), axis=1
                    )
    
                    # Combinar la tabla de logos y la tabla de métricas para la visualización final
                    tabla_final = pd.concat([logos_html, jugadores_comparativos_html])
    
                    # Convertir la tabla a formato HTML y personalizar el estilo
                    html_table = tabla_final.to_html(escape=False, classes='table table-bordered', border=0)
                    html_table = html_table.replace('<th>', '<th style="text-align: center;">')
    
                    # Mostrar la tabla final en la aplicación
                    st.write(html_table, unsafe_allow_html=True)
            else:
                st.error("No se encuentran todas las columnas necesarias ('Full name', 'Team logo', 'Team within selected timeframe') en los datos cargados.")
    else:
        st.error("Por favor, selecciona al menos una temporada.")
