import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Función para cargar datos CSV desde una URL
@st.cache_data
def cargar_csv_desde_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo desde {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# URLs de los archivos necesarios
url_metricas_traducidas = "https://github.com/CarlosCO94/911_Scouting/blob/main/Traducci%C3%B3n_Metricas.csv?raw=true"
url_logos_equipos = "https://github.com/CarlosCO94/911_Scouting/blob/main/Wyscout_Logo_URL.csv?raw=true"
url_datos_jugadores_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Cargar las métricas traducidas y los logos de equipos
metricas_traducidas_df = cargar_csv_desde_url(url_metricas_traducidas)
logos_equipos_df = cargar_csv_desde_url(url_logos_equipos)

# Convertir las métricas traducidas a un diccionario para una traducción rápida
diccionario_traducciones = dict(zip(metricas_traducidas_df['Métrica Original'], metricas_traducidas_df['Métrica Traducida']))

# Definición de las métricas por posición (en español)
metricas_por_posicion = {
    'Portero': ["Minutos jugados", "Goles concedidos por 90", "Tiros en contra por 90", "Porterías imbatidas", "Tasa de salvadas", 
                "xG en contra por 90", "Goles evitados por 90", "Pases hacia atrás recibidos como portero por 90", 
                "Salidas por 90", "Duelos aéreos por 90"],
    'Centrales': ["Minutos jugados", "Acciones defensivas exitosas por 90", "Duelos defensivos por 90", "Duelos aéreos por 90", 
                  "Entradas deslizantes por 90", "Tiros bloqueados por 90", "Intercepciones por 90", 
                  "Intercepciones ajustadas por posesión", "Pases hacia adelante por 90", "Pases filtrados por 90", 
                  "Goles de cabeza"],
    'Laterales': ["Minutos jugados", "Asistencias por 90", "Duelos por 90", "Duelos defensivos por 90", "Duelos aéreos por 90", 
                  "Tiros bloqueados por 90", "Intercepciones por 90", "Goles por 90", "Tiros por 90", "Centros por 90", 
                  "Regates por 90", "Duelos ofensivos por 90", "Pases hacia adelante por 90"],
    'Volantes Centrales + MCO': ["Minutos jugados", "Goles", "Asistencias por 90", "Duelos ganados", "Acciones defensivas exitosas por 90", 
                                 "Duelos defensivos por 90", "Pases largos por 90", "Duelos aéreos por 90", 
                                 "Intercepciones por 90", "Pases hacia adelante por 90", "Pases filtrados por 90"],
    'Delantero + Extremos': ["Minutos jugados", "Goles por 90", "Asistencias por 90", "Tiros por 90", "Tiros a puerta", 
                             "Regates exitosos por 90", "Duelos ofensivos por 90", "Pases recibidos por 90", 
                             "Centros por 90", "Regates por 90", "Pases precisos", "Pases hacia adelante por 90", 
                             "Pases filtrados por 90"]
}
# Función para cargar datos CSV de jugadores desde la URL base del repositorio
@st.cache_data
def cargar_datos_jugadores(url_base):
    file_urls = []
    try:
        response = requests.get(url_base)
        if response.status_code == 200:
            archivos = response.json()
            file_urls = [file['download_url'] for file in archivos if file['name'].endswith('.csv')]
        else:
            st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")
    
    data_by_season = {}
    available_seasons = set()
    
    for url in file_urls:
        data = cargar_csv_desde_url(url)
        if not data.empty:
            matches = re.findall(r'(\d{4}|\d{2}-\d{2})', url.split('/')[-1])
            if matches:
                for match in matches:
                    available_seasons.add(match)
            data_by_season[url.split('/')[-1]] = data

    return data_by_season, available_seasons

# Cargar datos de jugadores y obtener las temporadas disponibles
data_by_season, available_seasons = cargar_datos_jugadores(url_datos_jugadores_base)

# Aplicar traducciones a las columnas de cada DataFrame en data_by_season
for key in data_by_season:
    data_by_season[key].columns = [diccionario_traducciones.get(col, col) for col in data_by_season[key].columns]
# Verificar que hay temporadas disponibles
if not available_seasons:
    st.error("No se encontraron temporadas en los archivos CSV.")
else:
    selected_seasons = st.sidebar.multiselect("Selecciona el/los año(s) o temporada(s)", sorted(available_seasons))

    if selected_seasons:
        # Concatenar los datos de las temporadas seleccionadas
        filtered_data = pd.concat(
            [data for filename, data in data_by_season.items() if any(season in filename for season in selected_seasons)],
            ignore_index=True
        )

        if filtered_data.empty:
            st.error(f"No se encontraron datos para las temporadas seleccionadas: {', '.join(selected_seasons)}.")
        else:
            equipos_disponibles = filtered_data['Equipo en el periodo seleccionado'].unique()
            equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", ['Todos'] + sorted(equipos_disponibles))

            if equipo_seleccionado != 'Todos':
                filtered_data = filtered_data[filtered_data['Equipo en el periodo seleccionado'] == equipo_seleccionado]

            jugadores_comparacion = st.sidebar.multiselect(
                "Selecciona los jugadores para comparar (el primero será el jugador principal):", 
                filtered_data['Nombre completo'].unique()
            )

            if jugadores_comparacion:
                posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion]

                # Multiselect para seleccionar las métricas específicas del CSV
                todas_las_metricas = filtered_data.columns.tolist()
                metricas_seleccionadas = st.sidebar.multiselect("Selecciona las métricas a mostrar:", todas_las_metricas)

                metricas_combinar = metricas_filtradas + metricas_seleccionadas
                metricas_disponibles = [metrica for metrica in metricas_combinar if metrica in filtered_data.columns]

                # Advertencia si alguna métrica no está disponible
                metricas_no_disponibles = [metrica for metrica in metricas_combinar if metrica not in filtered_data.columns]
                if metricas_no_disponibles:
                    st.warning(f"Las siguientes métricas no están disponibles en los datos: {', '.join(metricas_no_disponibles)}")

                # Crear tabla de comparación de jugadores
                jugadores_comparativos = filtered_data.set_index('Nombre completo')[metricas_disponibles].transpose()

                # Añadir logos de equipos a la visualización
                logos_html = logos_equipos_df.set_index('Equipo')['Logo URL']
                jugadores_comparativos_html = jugadores_comparativos.applymap(
                    lambda x: f'<img src="{logos_html.get(x, "")}" width="50">' if x in logos_html else x
                )

                # Mostrar la tabla de comparación
                st.write(jugadores_comparativos_html.to_html(escape=False), unsafe_allow_html=True)
