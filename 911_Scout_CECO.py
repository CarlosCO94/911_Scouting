import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición
metricas_por_posicion = {
    'Portero': ["Matches played", "Minutes played", "Conceded goals per 90", "xG against per 90", "Prevented goals per 90", "Save rate, %", 
                "Exits per 90", "Aerial duels per 90", "Back passes received as GK per 90", 
                "Accurate passes, %", "Accurate forward passes, %", "Accurate long passes, %"],
    'Defensa': ["Matches played", "Minutes played", "Accelerations per 90", "Progressive runs per 90", "Aerial duels per 90", "Aerial duels won, %", 
                "Defensive duels won, %", "Duels won, %", "Sliding tackles per 90", "Interceptions per 90", 
                "Key passes per 90", "Short / medium passes per 90", "Forward passes per 90", "Long passes per 90", 
                "Passes per 90", "PAdj Interceptions", "Accurate passes to final third, %", "Accurate forward passes, %", 
                "Accurate back passes, %", "Accurate long passes, %", "Accurate passes, %"],
    'Lateral': ["Matches played", "Minutes played", "Successful attacking actions per 90", "Successful defensive actions per 90", "Accelerations per 90", 
                "Progressive runs per 90", "Crosses to goalie box per 90", "Crosses from final third per 90", 
                "Aerial duels won, %", "Offensive duels won, %", "Defensive duels won, %", "Defensive duels per 90", 
                "Duels won, %", "Interceptions per 90", "Passes per 90", "Forward passes per 90", 
                "Accurate passes to penalty area, %", "Received passes per 90", "Accurate passes to final third, %", 
                "Accurate through passes, %", "Accurate forward passes, %", "Accurate progressive passes, %", 
                "Third assists per 90", "xA per 90"],
    'Mediocampista': ["Matches played", "Minutes played", "Assists per 90", "xA per 90", "Offensive duels won, %", "Aerial duels won, %", 
                      "Defensive duels won, %", "Interceptions per 90", "Received passes per 90", 
                      "Accurate short / medium passes, %", "Accurate passes to final third, %", 
                      "Accurate long passes, %", "Accurate progressive passes, %", "Successful dribbles, %", 
                      "xG per 90", "Goals per 90"],
    'Extremos': ["Matches played", "Minutes played", "xG per 90", "Goals per 90", "Assists per 90", "xA per 90", "Received passes per 90", 
                 "Accurate crosses, %", "Accurate through passes, %", "Accurate progressive passes, %", 
                 "Crosses to goalie box per 90", "Accurate passes to penalty area, %", "Offensive duels won, %", 
                 "Defensive duels won, %", "Interceptions per 90", "Successful dribbles, %"],
    "Delantero": ["Matches played", "Minutes played", "Goals per 90", "Head goals per 90", "Non-penalty goals per 90", "Goal conversion, %", 
                  "xG per 90", "xA per 90", "Assists per 90", "Key passes per 90", "Passes per 90", 
                  "Passes to penalty area per 90", "Passes to final third per 90", "Accurate passes, %", 
                  "Accurate passes to final third, %", "Aerial duels won, %", "Duels won, %", 
                  "Shots per 90", "Shots on target, %", "Touches in box per 90"]
}

# Título de la aplicación
st.title("Comparación de Jugadores")

# URL de la carpeta Ligas en GitHub
url_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Ligas"

# Obtener la lista de archivos CSV en la carpeta Ligas
response = requests.get(url_base)
if response.status_code == 200:
    archivos = response.json()
    file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
else:
    st.error(f"Error al acceder a la carpeta Ligas: {response.status_code}")

# Cargar los archivos CSV desde el repositorio
data_by_season = {}
available_seasons = set()

for url in file_urls:
    response = requests.get(url)
    if response.status_code == 200:
        matches = re.findall(r'(\d{4}|\d{2}-\d{2})', url.split('/')[-1])
        if matches:
            for match in matches:
                available_seasons.add(match)
        data_by_season[url.split('/')[-1]] = pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")

# Verificar que hay temporadas disponibles
if not available_seasons:
    st.error("No se encontraron temporadas en los archivos CSV.")
else:
    selected_season = st.sidebar.selectbox("Selecciona el año o temporada", sorted(available_seasons))

    filtered_data = pd.concat(
        [data for filename, data in data_by_season.items() if selected_season in filename],
        ignore_index=True
    )

    if filtered_data.empty:
        st.error(f"No se encontraron datos para la temporada {selected_season}.")
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

            jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar (el primero será el jugador principal):", 
                                                           jugadores_filtrados_por_equipo['Full name'].unique())

            if jugadores_comparacion:
                jugador_principal = jugadores_comparacion[0]

                posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion]

                jugadores_filtrados = filtered_data[filtered_data['Full name'].isin(jugadores_comparacion)]

                logos_html = jugadores_filtrados[['Full name', 'Team logo']].drop_duplicates().set_index('Full name').T
                logos_html = logos_html.applymap(lambda url: f'<div style="text-align: center;"><img src="{url}" width="50"></div>')

                jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()

                logos_html.columns = jugadores_comparativos.columns

                jugadores_comparativos_html = jugadores_comparativos.apply(lambda row: row.apply(
                    lambda x: f'<div style="text-align: center; background-color: yellow; color: black;">{x}</div>' if x == row.max() else f'<div style="text-align: center;">{x}</div>'
                ), axis=1)

                tabla_final = pd.concat([logos_html, jugadores_comparativos_html])

                html_table = tabla_final.to_html(escape=False, classes='table table-bordered', border=0)
                html_table = html_table.replace('<th>', '<th style="text-align: center;">')

                st.write(html_table, unsafe_allow_html=True)

        else:
            st.error("No se encuentran todas las columnas necesarias ('Full name', 'Team logo', 'Team within selected timeframe') en los datos cargados.")
