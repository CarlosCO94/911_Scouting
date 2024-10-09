import streamlit as st
import pandas as pd
import re  # Para usar expresiones regulares

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición (sin cambios)
metricas_por_posicion = {
    'Portero': ["Conceded goals per 90", "xG against per 90", "Prevented goals per 90", "Save rate, %", 
                "Exits per 90", "Aerial duels per 90", "Back passes received as GK per 90", 
                "Accurate passes, %", "Accurate forward passes, %", "Accurate long passes, %"],
    'Defensa': ["Accelerations per 90", "Progressive runs per 90", "Aerial duels per 90", "Aerial duels won, %", 
                "Defensive duels won, %", "Duels won, %", "Sliding tackles per 90", "Interceptions per 90", 
                "Key passes per 90", "Short / medium passes per 90", "Forward passes per 90", "Long passes per 90", 
                "Passes per 90", "PAdj Interceptions", "Accurate passes to final third, %", "Accurate forward passes, %", 
                "Accurate back passes, %", "Accurate long passes, %", "Accurate passes, %"],
    'Lateral': ["Successful attacking actions per 90", "Successful defensive actions per 90", "Accelerations per 90", 
                "Progressive runs per 90", "Crosses to goalie box per 90", "Crosses from final third per 90", 
                "Aerial duels won, %", "Offensive duels won, %", "Defensive duels won, %", "Defensive duels per 90", 
                "Duels won, %", "Interceptions per 90", "Passes per 90", "Forward passes per 90", 
                "Accurate passes to penalty area, %", "Received passes per 90", "Accurate passes to final third, %", 
                "Accurate through passes, %", "Accurate forward passes, %", "Accurate progressive passes, %", 
                "Third assists per 90", "xA per 90"],
    'Mediocampista': ["Assists per 90", "xA per 90", "Offensive duels won, %", "Aerial duels won, %", 
                      "Defensive duels won, %", "Interceptions per 90", "Received passes per 90", 
                      "Accurate short / medium passes, %", "Accurate passes to final third, %", 
                      "Accurate long passes, %", "Accurate progressive passes, %", "Successful dribbles, %", 
                      "xG per 90", "Goals per 90"],
    'Extremos': ["xG per 90", "Goals per 90", "Assists per 90", "xA per 90", "Received passes per 90", 
                 "Accurate crosses, %", "Accurate through passes, %", "Accurate progressive passes, %", 
                 "Crosses to goalie box per 90", "Accurate passes to penalty area, %", "Offensive duels won, %", 
                 "Defensive duels won, %", "Interceptions per 90", "Successful dribbles, %"],
    "Delantero": ["Goals per 90", "Head goals per 90", "Non-penalty goals per 90", "Goal conversion, %", 
                  "xG per 90", "xA per 90", "Assists per 90", "Key passes per 90", "Passes per 90", 
                  "Passes to penalty area per 90", "Passes to final third per 90", "Accurate passes, %", 
                  "Accurate passes to final third, %", "Aerial duels won, %", "Duels won, %", 
                  "Shots per 90", "Shots on target, %", "Touches in box per 90"]
    # Otros roles omitidos por brevedad...
}

# Título de la aplicación
st.title("Comparación de Jugadores")

# URL del repositorio de GitHub
github_repo_url = "https://raw.githubusercontent.com/tu_usuario/tu_repositorio/main/"  # Cambia esto a tu URL

# Lista de archivos CSV en el repositorio
archivos_csv = ["archivo1.csv", "archivo2.csv"]  # Cambia esto a los nombres de tus archivos

# Crear una lista de URLs de los archivos CSV
urls_archivos = [github_repo_url + archivo for archivo in archivos_csv]

# Extraer las temporadas y años de los nombres de los archivos y crear un diccionario para almacenar los datos por temporada
data_by_season = {}
available_seasons = set()

for url in urls_archivos:
    # Usar una expresión regular para encontrar años y temporadas en el nombre del archivo (ejemplo: 2020, 2021, 22-23, 23-24)
    matches = re.findall(r'(\d{4}|\d{2}-\d{2})', url)
    if matches:
        for match in matches:
            if '-' in match:  # Si es del tipo '22-23', lo mantenemos como está
                available_seasons.add(match)
            else:  # Si es del tipo '2020' o similar
                available_seasons.add(match)
    
    # Leer el archivo desde la URL y agregarlo al diccionario según la temporada
    data_by_season[url] = pd.read_csv(url)

# Añadir un filtro de temporada en la barra lateral basado en los años y temporadas encontrados
selected_season = st.sidebar.selectbox("Selecciona el año o temporada", sorted(available_seasons))

# Combinar todos los datos correspondientes a la temporada seleccionada
filtered_data = pd.concat(
    [data for url, data in data_by_season.items() if selected_season in url], ignore_index=True
)

# Verificar si las columnas necesarias están en los datos
if 'Full name' in filtered_data.columns and 'Team logo' in filtered_data.columns and 'Team within selected timeframe' in filtered_data.columns:
    # Seleccionar el jugador principal para la comparación
    jugador_principal = st.sidebar.selectbox("Selecciona el jugador principal:", filtered_data['Full name'].unique())

    # Seleccionar varios jugadores para comparar con el jugador principal, asegurando que el jugador principal siempre esté incluido
    jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar:", 
                                                   filtered_data['Full name'].unique(), 
                                                   default=[jugador_principal])

    # Asegurar que el jugador principal esté en la lista de comparación y en la segunda columna
    if jugador_principal not in jugadores_comparacion:
        jugadores_comparacion.insert(0, jugador_principal)
    else:
        jugadores_comparacion.remove(jugador_principal)
        jugadores_comparacion.insert(0, jugador_principal)

    # Seleccionar la posición para filtrar las métricas
    posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())

    # Filtrar las métricas de acuerdo a la posición seleccionada
    metricas_filtradas = metricas_por_posicion[posicion]

    # Filtrar los datos para mostrar solo los jugadores seleccionados y las métricas relevantes
    jugadores_filtrados = filtered_data[filtered_data['Full name'].isin(jugadores_comparacion)]

    # Crear una fila con los logos del equipo y centrarlos en HTML
    logos_html = jugadores_filtrados[['Full name', 'Team logo']].drop_duplicates().set_index('Full name').T
    logos_html = logos_html.applymap(lambda url: f'<div style="text-align: center;"><img src="{url}" width="50"></div>')

    # Reorganizar la tabla para que los jugadores sean columnas y las métricas sean filas
    jugadores_comparativos = jugadores_filtrados.set_index('Full name')[metricas_filtradas].transpose()

    # Asegurar que los índices de logos_html y jugadores_comparativos sean únicos y estén alineados
    logos_html.columns = jugadores_comparativos.columns

    # Aplicar formato condicional para resaltar la métrica más alta con un fondo amarillo y texto negro
    jugadores_comparativos_html = jugadores_comparativos.apply(lambda row: row.apply(
        lambda x: f'<div style="text-align: center; background-color: yellow; color: black;">{x}</div>' if x == row.max() else f'<div style="text-align: center;">{x}</div>'
    ), axis=1)

    # Combinar la fila de logos con la tabla de métricas
    tabla_final = pd.concat([logos_html, jugadores_comparativos_html])

    # Convertir la tabla a HTML con encabezados centrados
    html_table = tabla_final.to_html(escape=False, classes='table table-bordered', border=0)
    html_table = html_table.replace('<th>', '<th style="text-align: center;">')

    # Mostrar la tabla con estilo centrado para encabezados y contenido
    st.write(html_table, unsafe_allow_html=True)
else:
    st.error("No se encuentran todas las columnas necesarias ('Full name', 'Team logo', 'Team within selected timeframe') en los datos cargados.")
