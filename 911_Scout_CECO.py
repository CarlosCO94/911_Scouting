import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Métricas por posición en español
metricas_por_posicion = {
    'Portero': [
        "Minutos jugados", "Goles concedidos por 90", "Disparos contra por 90", "Porterías a cero",
        "Tasa de salvadas, %", "xG contra por 90", "Goles prevenidos por 90", "Pases hacia atrás recibidos como portero por 90",
        "Salidas por 90", "Duelos aéreos por 90"
    ],
    'Centrales': [
        "Minutos jugados", "Acciones defensivas exitosas por 90", "Duelos defensivos por 90", "Duelos aéreos por 90",
        "Entradas por deslizamiento por 90", "PAdj Entradas por deslizamiento", "Disparos bloqueados por 90",
        "Intercepciones por 90", "PAdj Intercepciones", "Pases hacia adelante por 90", "Pases filtrados por 90",
        "Goles de cabeza"
    ],
    'Laterales': [
        "Minutos jugados", "Asistencias por 90", "Duelos por 90", "Duelos defensivos por 90", "Duelos aéreos por 90",
        "Disparos bloqueados por 90", "Intercepciones por 90", "Goles por 90", "Disparos por 90",
        "Centros por 90", "Regates por 90", "Duelos ofensivos por 90", "Pases hacia adelante por 90"
    ],
    'Volantes Centrales + MCO': [
        "Minutos jugados", "Goles", "Asistencias por 90", "Duelos ganados, %", "Acciones defensivas exitosas por 90",
        "Duelos defensivos por 90", "Pases largos por 90", "Duelos aéreos por 90",
        "Intercepciones por 90", "Pases hacia adelante por 90", "Pases filtrados por 90"
    ],
    'Delantero + Extremos': [
        "Minutos jugados", "Goles por 90", "Asistencias por 90", "Disparos por 90", "Disparos a puerta, %",
        "Regates exitosos, %", "Duelos ofensivos por 90", "Pases recibidos por 90",
        "Centros por 90", "Regates por 90", "Pases precisos, %", "Pases hacia adelante por 90",
        "Pases filtrados por 90"
    ]
}

# Título de la aplicación
st.title("Comparación de Jugadores")

# Cargar CSV de métricas traducidas y logos
metricas_traducidas_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Traducci%C3%B3n_Metricas.csv"
logos_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Wyscout_Logo_URL.csv"

metricas_traducidas_df = pd.read_csv(metricas_traducidas_url)
logos_df = pd.read_csv(logos_url)

# Crear diccionario de traducciones
diccionario_traducciones = dict(zip(metricas_traducidas_df['Métrica Original'], metricas_traducidas_df['Métrica Traducida']))

# Función para traducir métricas al español usando el diccionario cargado
def traducir_metricas(metrica):
    return diccionario_traducciones.get(metrica, metrica)

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
                available_seasons.add(match)
        data_by_season[url.split('/')[-1]] = data

# Verificar que hay temporadas disponibles
if not available_seasons:
    st.error("No se encontraron temporadas en los archivos CSV.")
else:
    selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", sorted(available_seasons))

    if selected_seasons:
        filtered_data = pd.concat(
            [data for filename, data in data_by_season.items() if any(season in filename for season in selected_seasons)],
            ignore_index=True
        )

        if filtered_data.empty:
            st.error(f"No se encontraron datos para las temporadas seleccionadas: {', '.join(selected_seasons)}.")
        else:
            st.write("Columnas disponibles en el DataFrame:", [traducir_metricas(col) for col in filtered_data.columns])

            equipos_disponibles = ['Todos'] + sorted(filtered_data['Equipo durante el período seleccionado'].unique())
            equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", equipos_disponibles)

            if equipo_seleccionado != 'Todos':
                jugadores_filtrados_por_equipo = filtered_data[filtered_data['Equipo durante el período seleccionado'] == equipo_seleccionado]
            else:
                jugadores_filtrados_por_equipo = filtered_data

            jugadores_comparacion = st.sidebar.multiselect(
                "Selecciona los jugadores para comparar (el primero será el jugador principal):", 
                jugadores_filtrados_por_equipo['Nombre completo'].unique()
            )

            if jugadores_comparacion:
                posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion]

                # Multiselect para seleccionar las métricas específicas del CSV
                metricas_seleccionadas = st.sidebar.multiselect("Selecciona las métricas a mostrar:", metricas_filtradas)
                jugadores_filtrados = jugadores_filtrados_por_equipo[jugadores_filtrados_por_equipo['Nombre completo'].isin(jugadores_comparacion)]

                metricas_combinar = metricas_filtradas + metricas_seleccionadas
                metricas_disponibles = [metrica for metrica in metricas_combinar if metrica in jugadores_filtrados.columns]

                jugadores_comparativos = jugadores_filtrados.set_index('Nombre completo')[metricas_disponibles].transpose()

                logos_html = jugadores_filtrados[['Nombre completo', 'Logo del equipo']].drop_duplicates().set_index('Nombre completo').T
                logos_html = logos_html.applymap(lambda url: f'<div style="text-align: center;"><img src="{url}" width="50"></div>')

                logos_html.columns = jugadores_comparativos.columns

                jugadores_comparativos_html = jugadores_comparativos.apply(
                    lambda row: row.apply(
                        lambda x: f'<div style="text-align: center; background-color: yellow; color: black;">{x}</div>' if x == row.max() else f'<div style="text-align: center;">{x}</div>'
                    ), axis=1
                )

                tabla_final = pd.concat([logos_html, jugadores_comparativos_html])

                html_table = tabla_final.to_html(escape=False, classes='table table-bordered', border=0)
                html_table = html_table.replace('<th>', '<th style="text-align: center;">')

                st.write(html_table, unsafe_allow_html=True)


