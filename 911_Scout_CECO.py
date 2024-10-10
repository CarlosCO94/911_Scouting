import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Función para traducir métricas al español
def traducir_metricas(metrica):
    traducciones = {
        "Player": "Jugador",
        "Full name": "Nombre completo",
        "Wyscout id": "ID Wyscout",
        "Team": "Equipo",
        "Team within selected timeframe": "Equipo en el periodo seleccionado",
        "Team logo": "Logo del equipo",
        "Competition": "Competencia",
        "Position": "Posición",
        "Primary position": "Posición principal",
        "Primary position, %": "Porcentaje en posición principal",
        "Secondary position": "Posición secundaria",
        "Secondary position, %": "Porcentaje en posición secundaria",
        "Third position": "Tercera posición",
        "Third position, %": "Porcentaje en tercera posición",
        "Age": "Edad",
        "Birthday": "Fecha de nacimiento",
        "Market value": "Valor de mercado",
        "Contract expires": "Fin del contrato",
        "Matches played": "Partidos jugados",
        "Minutes played": "Minutos jugados",
        "Goals": "Goles",
        "xG": "xG (Goles esperados)",
        "Assists": "Asistencias",
        "xA": "xA (Asistencias esperadas)",
        "Duels per 90": "Duelos por 90",
        "Duels won, %": "Duelos ganados, %",
        "Successful defensive actions per 90": "Acciones defensivas exitosas por 90",
        "Defensive duels per 90": "Duelos defensivos por 90",
        "Defensive duels won, %": "Duelos defensivos ganados, %",
        "Aerial duels per 90": "Duelos aéreos por 90",
        "Aerial duels won, %": "Duelos aéreos ganados, %",
        "Sliding tackles per 90": "Entradas deslizantes por 90",
        "PAdj Sliding tackles": "Entradas deslizantes ajustadas por posesión",
        "Shots blocked per 90": "Tiros bloqueados por 90",
        "Interceptions per 90": "Intercepciones por 90",
        "PAdj Interceptions": "Intercepciones ajustadas por posesión",
        "Fouls per 90": "Faltas por 90",
        "Yellow cards": "Tarjetas amarillas",
        "Yellow cards per 90": "Tarjetas amarillas por 90",
        "Red cards": "Tarjetas rojas",
        "Red cards per 90": "Tarjetas rojas por 90",
        "Successful attacking actions per 90": "Acciones ofensivas exitosas por 90",
        "Goals per 90": "Goles por 90",
        "Non-penalty goals": "Goles sin penalti",
        "Non-penalty goals per 90": "Goles sin penalti por 90",
        "xG per 90": "xG por 90",
        "Head goals": "Goles de cabeza",
        "Head goals per 90": "Goles de cabeza por 90",
        "Shots": "Tiros",
        "Shots per 90": "Tiros por 90",
        "Shots on target, %": "Tiros a puerta, %",
        "Goal conversion, %": "Conversión de goles, %",
        "Assists per 90": "Asistencias por 90",
        "Crosses per 90": "Centros por 90",
        "Accurate crosses, %": "Centros precisos, %",
        "Crosses to goalie box per 90": "Centros al área pequeña por 90",
        "Dribbles per 90": "Regates por 90",
        "Successful dribbles, %": "Regates exitosos, %",
        "Offensive duels per 90": "Duelos ofensivos por 90",
        "Offensive duels won, %": "Duelos ofensivos ganados, %",
        "Touches in box per 90": "Toques en el área por 90",
        "Progressive runs per 90": "Carreras progresivas por 90",
        "Accelerations per 90": "Aceleraciones por 90",
        "Received passes per 90": "Pases recibidos por 90",
        "Passes per 90": "Pases por 90",
        "Accurate passes, %": "Pases precisos, %",
        "Forward passes per 90": "Pases hacia adelante por 90",
        "Accurate forward passes, %": "Pases hacia adelante precisos, %",
        "Through passes per 90": "Pases filtrados por 90",
        "Accurate through passes, %": "Pases filtrados precisos, %",
        "Progressive passes per 90": "Pases progresivos por 90",
        "Accurate progressive passes, %": "Pases progresivos precisos, %",
        "Conceded goals": "Goles concedidos",
        "Conceded goals per 90": "Goles concedidos por 90",
        "Clean sheets": "Porterías imbatidas",
        "Save rate, %": "Tasa de salvadas, %",
        "xG against": "xG en contra",
        "xG against per 90": "xG en contra por 90",
        "Prevented goals": "Goles evitados",
        "Prevented goals per 90": "Goles evitados por 90"
    }
    return traducciones.get(metrica, metrica)

metricas_por_posicion = {
    'Portero': [
        "Minutes played", "Conceded goals per 90", "Shots against per 90", 
        "Clean sheets", "Save rate, %", "xG against per 90", "Prevented goals per 90", 
        "Back passes received as GK per 90", "Exits per 90", "Aerial duels per 90"
    ],
    'Centrales': [
        "Minutes played", "Successful defensive actions per 90", "Defensive duels per 90", 
        "Aerial duels per 90", "Sliding tackles per 90", "Shots blocked per 90", 
        "Interceptions per 90", "PAdj Interceptions", "Forward passes per 90", 
        "Through passes per 90", "Head goals"
    ],
    'Laterales': [
        "Minutes played", "Assists per 90", "Duels per 90", "Defensive duels per 90", 
        "Aerial duels per 90", "Shots blocked per 90", "Interceptions per 90", 
        "Goals per 90", "Shots per 90", "Crosses per 90", "Dribbles per 90", 
        "Offensive duels per 90", "Forward passes per 90"
    ],
    'Volantes Centrales + MCO': [
        "Minutes played", "Goals", "Assists per 90", "Duels won, %", 
        "Successful defensive actions per 90", "Defensive duels per 90", 
        "Long passes per 90", "Aerial duels per 90", "Interceptions per 90", 
        "Forward passes per 90", "Through passes per 90"
    ],
    'Delantero + Extremos': [
        "Minutes played", "Goals per 90", "Assists per 90", "Shots per 90", 
        "Shots on target, %", "Successful dribbles per 90", "Offensive duels per 90", 
        "Received passes per 90", "Crosses per 90", "Dribbles per 90", 
        "Accurate passes, %", "Forward passes per 90", "Through passes per 90"
    ]
}
# Inicializar file_urls
file_urls = []

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
else:
    data_by_season = {}
    available_seasons = set()

    for url in file_urls:
        data = cargar_datos_csv(url)
        if not data.empty:
            data.columns = [traducir_metricas(col) for col in data.columns]  # Traducir columnas
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

            # Selección de equipo y jugadores
            if 'Nombre completo' in filtered_data.columns and 'Logo del equipo' in filtered_data.columns and 'Equipo en el periodo seleccionado' in filtered_data.columns:
                equipos_disponibles = filtered_data['Equipo en el periodo seleccionado'].unique()
                equipos_disponibles = ['Todos'] + sorted(equipos_disponibles)
                equipo_seleccionado = st.sidebar.selectbox("Selecciona el equipo", equipos_disponibles)

                if equipo_seleccionado == 'Todos':
                    jugadores_filtrados_por_equipo = filtered_data
                else:
                    jugadores_filtrados_por_equipo = filtered_data[filtered_data['Equipo en el periodo seleccionado'] == equipo_seleccionado]

                jugadores_comparacion = st.sidebar.multiselect("Selecciona los jugadores para comparar:", jugadores_filtrados_por_equipo['Nombre completo'].unique())

                if jugadores_comparacion:
                    posicion = st.sidebar.selectbox("Selecciona la posición para mostrar las métricas correspondientes:", metricas_por_posicion.keys())
                    metricas_filtradas = metricas_por_posicion[posicion]

                    # Multiselect para seleccionar las métricas específicas del CSV
                    todas_las_metricas = filtered_data.columns.tolist()
                    metricas_seleccionadas = st.sidebar.multiselect("Selecciona las métricas a mostrar:", todas_las_metricas)

                    metricas_combinar = metricas_filtradas + metricas_seleccionadas
                    metricas_disponibles = [metrica for metrica in metricas_combinar if metrica in jugadores_filtrados_por_equipo.columns]

                    # Advertencia si alguna métrica no está disponible
                    metricas_no_disponibles = [metrica for metrica in metricas_combinar if metrica not in jugadores_filtrados_por_equipo.columns]
                    if metricas_no_disponibles:
                        st.warning(f"Las siguientes métricas no están disponibles en los datos: {', '.join(metricas_no_disponibles)}")

                    # Crear tabla de comparación de jugadores
                    jugadores_comparativos = jugadores_filtrados_por_equipo.set_index('Nombre completo')[metricas_disponibles].transpose()

                    # Mostrar la tabla
                    st.write(jugadores_comparativos)
