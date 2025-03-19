import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import io
import pandas as pd
import math
import matplotlib.patches as patches
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from mplsoccer import PyPizza
from scipy.stats import percentileofscore
from io import BytesIO
from scipy import stats
from math import pi
from matplotlib.patches import FancyArrowPatch

# Intenta importar desde config.py, si no existe usamos variables locales
try:
    from config import (
        METRICS_BY_POSITION,
        BASE_URLS,
        FILE_NAMES_FALLBACK,
        COMMON_COLUMNS,
        POSITION_PATTERNS,
        CHART_COLORS,
        CATEGORY_COLORS,
        APP_CONFIG
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # Fallback a las definiciones originales
    # Aquí irían las definiciones originales si config.py no está disponible
    METRICS_BY_POSITION = {
        'Portero': [
            ("Matches played", "Partidos jugados", "General"),
            ("Minutes played", "Minutos jugados", "General"),
            # ... resto de métricas de Portero
        ],
        # ... resto de posiciones
    }
    
    BASE_URLS = {
        "2020": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2020",
        "20-21": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/20-21",
        "2021": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2021",
        "21-22": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/21-22",
        "2022": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2022",
        "22-23": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/22-23",
        "2023": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2023",
        "23-24": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/23-24",
        "2024": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2024",
        "24-25": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/24-25",
        "2025": "https://raw.githubusercontent.com/CarlosCO94/Scout_911/main/data/2025"
    }
    
    # Simplificado para el fallback
    FILE_NAMES_FALLBACK = {
        "2024": [
            "Argentina Copa de la Liga 2024.parquet",
            "Peruvian Liga 1 2024.parquet",
        ],
        # ... otras temporadas simplificadas
    }
    
    # Columnas comunes
    COMMON_COLUMNS = [
        "Player", "Team within selected timeframe", "Passport country",
        "Foot", "Age", "Minutes played", "Primary position", "Contract expires",
        "Position", "Matches played"
    ]
    
    # Patrones de posición
    POSITION_PATTERNS = {
        'Portero': 'GK', 'Defensa': 'CB',
        'Lateral Izquierdo': 'LB|LWB', 'Lateral Derecho': 'RB|RWB',
        'Mediocampista Defensivo': 'DMF', 'Mediocampista Central': 'CMF',
        'Mediocampista Ofensivo': 'AMF', 'Extremos': 'RW|LW|LWF|RWF',
        'Delantero': 'CF'
    }
    
    # Colores para gráficos
    CHART_COLORS = {
        "primary": "#1A78CF",      # Azul principal
        "secondary": "#FF9300",    # Naranja secundario
        "tertiary": "#FF6347",     # Rojo terciario
        "quaternary": "#32CD32",   # Verde cuaternario
    }
    
    # Colores por categoría
    CATEGORY_COLORS = {
        "General": "#1A78CF",      # Azul
        "Defensa": "#FF9300",      # Naranja
        "Pases": "#FF6347",        # Rojo
        "Ataque": "#32CD32"        # Verde
    }
    
    # Configuración de la app
    APP_CONFIG = {
        "title": "Deportivo Garcilaso ⚽️",
        "icon": "⚽🐈‍⬛🇵🇪📊",
        "layout": "wide",
        "version": "2.0.0",
        "author": "Deportivo Garcilaso",
        "last_update": "Marzo 2025",
        "auto_detect_leagues": True
    }

# Intenta importar el detector de ligas
try:
    from utils.league_detector import get_available_leagues
    LEAGUE_DETECTOR_AVAILABLE = True
except ImportError:
    LEAGUE_DETECTOR_AVAILABLE = False

# Intenta importar funciones de optimización
try:
    from utils.data_loader import load_parquet_data, optimize_dataframe
    DATA_LOADER_AVAILABLE = True
except ImportError:
    DATA_LOADER_AVAILABLE = False
    
    # Implementación local si no está disponible el módulo
    @st.cache_data(ttl=3600)
    def load_parquet_data(file_url, season=None, competition=None, columns=None):
        """
        Carga un archivo Parquet desde una URL con mejoras.
        """
        try:
            response = requests.get(file_url, timeout=30)
            if response.status_code == 200:
                file_bytes = BytesIO(response.content)
                
                # Intentar cargar con columnas específicas o todas
                try:
                    if columns:
                        data = pd.read_parquet(file_bytes, columns=columns)
                    else:
                        data = pd.read_parquet(file_bytes)
                except Exception as e:
                    if columns:  # Solo mostrar advertencia si se intentó cargar columnas específicas
                        st.warning(f"Error al cargar columnas específicas. Cargando todas: {e}")
                    file_bytes.seek(0)  # Resetear el buffer
                    data = pd.read_parquet(file_bytes)
                
                # Agregar columnas adicionales
                if season is not None:
                    data["Season"] = season
                if competition is not None:
                    data["Competition"] = competition
                    
                return data
            else:
                st.error(f"Error al descargar {file_url}: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Error al procesar {file_url}: {e}")
            return None

    def optimize_dataframe(df):
        """
        Optimiza los tipos de datos de un DataFrame para reducir memoria.
        """
        # Convertir columnas categóricas
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() < df.shape[0] * 0.5:  # Si menos del 50% son valores únicos
                df[col] = df[col].astype('category')
        
        # Optimizar floats
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = df[col].astype('float32')
            
        return df

# Implementación local del detector de ligas si no está disponible
if not LEAGUE_DETECTOR_AVAILABLE:
    @st.cache_data(ttl=3600*6)  # Cache por 6 horas
    def detect_leagues_for_season(base_url, season):
        """
        Detecta automáticamente las ligas disponibles para una temporada específica.
        """
        # Lista de patrones comunes para probar
        common_leagues = [
            "Argentina Copa de la Liga",
            "Argentina Primera Nacional",
            "Argentina LPF",
            "Bolivian LFPB",
            "Brasileirao",
            "Brazil Serie B",
            "Brazil Serie C",
            "Canadian Premier League",
            "Chilean Primera B",
            "Chilean Primera Division",
            "Colombian Primera A",
            "Colombian Torneo BetPlay",
            "Ecuador Liga Pro",
            "J1",
            "K League 1",
            "MLS",
            "MLS Next Pro",
            "Panama LPF",
            "Paraguay Division Profesional",
            "Peruvian Liga 1",
            "USL Championship",
            "USL League 1",
            "Uruguay Primera Division",
            "Premier League",
            "La Liga",
            "Bundesliga",
            "Serie A",
            "Ligue 1"
        ]
        
        # Para temporadas tipo 20-21, tenemos más ligas
        if "-" in season:
            additional_leagues = [
                "Belgian Pro League",
                "Championship",
                "Costa Rican Primera Division",
                "El Salvador Primera Division",
                "English National League",
                "Eredivisie",
                "French National 1",
                "Greek Super League",
                "Guatemalan Liga Nacional",
                "Honduran Liga Nacional",
                "La Liga 2",
                "League One",
                "League Two",
                "Liga MX",
                "Liga de Expansion MX",
                "Ligue 2",
                "Nicaragua Primera Division",
                "Portuguese Segunda Liga",
                "Primavera 1",
                "Primeira Liga",
                "Russian First League",
                "Russian Premier League",
                "Saudi Pro League",
                "Scottish Championship",
                "Serie B",
                "Serie C",
                "Super Lig",
                "Superliga",
                "Swiss Challenge League",
                "Swiss Super League",
                "UAE Pro League"
            ]
            common_leagues.extend(additional_leagues)
        
        # Función para verificar si existe un archivo
        def check_file(league_name):
            # Construir nombre de archivo
            file_name = f"{league_name} {season}.parquet"
            url = f"{base_url}/{file_name}"
            
            try:
                # Usar 'head' para verificar existencia sin descargar el archivo completo
                response = requests.head(url, timeout=2)
                
                if response.status_code == 200:
                    return file_name
                return None
            except:
                return None
        
        # Verificar archivos en paralelo para mayor velocidad
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(check_file, common_leagues))
        
        # Filtrar resultados None
        available_files = [f for f in results if f is not None]
        
        return sorted(available_files)

    @st.cache_data(ttl=3600*24)  # Cache por 24 horas
    def get_available_leagues():
        """
        Obtiene todas las ligas disponibles para todas las temporadas definidas.
        """
        # Usamos el fallback como base
        detected_file_names = FILE_NAMES_FALLBACK.copy()
        
        # Crear barra de progreso para la UI
        progress_placeholder = st.empty()
        progress_bar = None
        total_seasons = len(BASE_URLS)
        
        try:
            # Mostrar progreso solo si estamos en una sesión de Streamlit
            progress_placeholder.text("Detectando ligas disponibles...")
            progress_bar = st.progress(0)
        except:
            pass
        
        # Detectar ligas para cada temporada
        for i, (season, base_url) in enumerate(BASE_URLS.items()):
            # Actualizar progreso
            if progress_bar:
                progress_bar.progress((i) / total_seasons)
            
            # Detectar ligas
            detected_leagues = detect_leagues_for_season(base_url, season)
            
            # Si encontramos algo, actualizar el diccionario
            if detected_leagues:
                detected_file_names[season] = detected_leagues
            
            # Actualizar progreso
            if progress_bar:
                progress_bar.progress((i + 1) / total_seasons)
        
        # Limpiar UI
        if progress_placeholder:
            progress_placeholder.empty()
        if progress_bar:
            progress_bar.empty()
        
        return detected_file_names

# Función para obtener la lista de archivos (ligas)
def get_file_names():
    """
    Obtiene la lista de archivos disponibles, ya sea de forma dinámica o estática.
    """
    # Si ya tenemos los nombres de archivos en la sesión, usarlos
    if "file_names" in st.session_state and st.session_state.file_names is not None:
        return st.session_state.file_names

    # Si la detección automática está habilitada
    if APP_CONFIG.get("auto_detect_leagues", True):
        try:
            # Mostrar un mensaje mientras se detectan las ligas
            with st.spinner("Detectando ligas disponibles..."):
                file_names = get_available_leagues()
                st.session_state.file_names = file_names
                return file_names
        except Exception as e:
            st.warning(f"No se pudieron detectar las ligas automáticamente: {e}")
            # Usar fallback en caso de error
            st.session_state.file_names = FILE_NAMES_FALLBACK
            return FILE_NAMES_FALLBACK
    else:
        # Usar la lista estática
        st.session_state.file_names = FILE_NAMES_FALLBACK
        return FILE_NAMES_FALLBACK

# Configuración básica de la página
st.set_page_config(
    page_title=APP_CONFIG.get("title", "Deportivo Garcilaso ⚽️"),
    layout=APP_CONFIG.get("layout", "wide"),
    page_icon=APP_CONFIG.get("icon", "⚽🐈‍⬛🇵🇪📊"),
    initial_sidebar_state="expanded"
)

# Inicialización de estado de sesión para tracking de navegación y datos
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.data_loaded = False
    st.session_state.filtered_data = None
    st.session_state.file_names = None

# Función principal para cargar datos
def main_page():
    st.title(APP_CONFIG.get("title", "Deportivo Garcilaso ⚽️"))
    st.write("Análisis de datos Propio | Rival | Scouting.")

    # Obtener nombres de archivos (ligas) disponibles
    file_names = get_file_names()

    # Crear columnas para los filtros
    col1, col2 = st.columns(2)
    
    with col1:
        # Selección de temporadas
        available_seasons = list(BASE_URLS.keys())
        select_all_seasons = st.checkbox("Seleccionar todas las temporadas", value=True)
        
        if select_all_seasons:
            selected_seasons = available_seasons
        else:
            selected_seasons = st.multiselect(
                "Selecciona temporadas:", 
                available_seasons, 
                default=[]
            )
    
    # Filtrar archivos por temporada seleccionada
    all_files = []
    for season in selected_seasons:
        if season in file_names:  # Verificar que la temporada existe en file_names
            for file in file_names[season]:
                all_files.append((
                    season, 
                    f"{BASE_URLS[season]}/{file}".replace(" ", "%20"), 
                    file.split(".")[0]
                ))
    
    with col2:
        # Opción para mostrar/seleccionar todas las ligas
        select_all_leagues = st.checkbox("Seleccionar todas las ligas", value=True)
        
        # Contador para mostrar número de ligas disponibles
        st.write(f"Ligas disponibles: {len(all_files)}")
        
        if select_all_leagues:
            selected_files = all_files
        else:
            # Agrupar por temporada para mejor organización
            leagues_by_season = {}
            for season, _, file in all_files:
                if season not in leagues_by_season:
                    leagues_by_season[season] = []
                leagues_by_season[season].append(f"{season} - {file}")
            
            # Crear un expander por temporada
            selected_leagues = []
            for season, leagues in sorted(leagues_by_season.items()):
                with st.expander(f"Ligas {season}"):
                    for league in sorted(leagues):
                        if st.checkbox(league, key=f"league_{league}"):
                            selected_leagues.append(league)
            
            # Convertir selecciones a formato compatible
            selected_files = [
                (season, file_url, competition)
                for season, file_url, competition in all_files
                if f"{season} - {competition}" in selected_leagues
            ]

    # Opciones avanzadas de carga
    with st.expander("Opciones avanzadas de carga"):
        load_columns = st.checkbox("Cargar solo columnas esenciales (más rápido)", value=True)
        columns_to_load = None
        if load_columns:
            columns_to_load = COMMON_COLUMNS.copy()
            # Opción para añadir métricas específicas
            st.write("Selecciona métricas adicionales a cargar:")
            
            # Agrupar métricas por categoría
            metrics_by_category = {}
            for position_metrics in METRICS_BY_POSITION.values():
                for metric in position_metrics:
                    category = metric[2]  # General, Defensa, Pases, Ataque
                    if category not in metrics_by_category:
                        metrics_by_category[category] = set()
                    metrics_by_category[category].add((metric[0], metric[1]))  # (nombre_inglés, nombre_español)
            
            # Mostrar métricas por categoría en columnas
            cols = st.columns(len(metrics_by_category))
            additional_metrics = []
            
            for i, (category, metrics) in enumerate(metrics_by_category.items()):
                with cols[i]:
                    st.write(f"**{category}**")
                    for metric_en, metric_es in sorted(metrics):
                        if st.checkbox(metric_es, key=f"metric_{metric_en}"):
                            additional_metrics.append(metric_en)
            
            if additional_metrics:
                columns_to_load.extend(additional_metrics)

        # Opción para forzar detección de ligas
        if st.button("Refrescar lista de ligas disponibles"):
            with st.spinner("Detectando ligas..."):
                file_names = get_available_leagues()
                st.session_state.file_names = file_names
                st.experimental_rerun()

    # Botón para cargar datos
    if st.button("Cargar Datos", key="load_data_button"):
        # Verificar si hay archivos seleccionados
        if not selected_files:
            st.warning("No se han seleccionado archivos para cargar.")
            return
            
        # Crear una columna para el progreso
        progress_container = st.empty()
        with progress_container.container():
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            progress_text.text(f"Iniciando carga de {len(selected_files)} archivos...")
            
            # Cargar archivos con mejor manejo de progreso
            total_files = len(selected_files)
            dataframes = []
            
            for i, (season, file_url, competition) in enumerate(selected_files):
                # Actualizar texto de progreso
                progress_text.text(f"Cargando archivo {i+1}/{total_files}: {competition}")
                progress_bar.progress((i / total_files))
                
                # Cargar archivo
                df = load_parquet_data(
                    file_url, 
                    season=season, 
                    competition=competition,
                    columns=columns_to_load
                )
                
                if df is not None:
                    # Optimizar el DataFrame inmediatamente
                    df = optimize_dataframe(df)
                    dataframes.append(df)
            
            # Concatenar datos
            if dataframes:
                progress_text.text("Procesando datos...")
                progress_bar.progress(0.95)  # Casi completo
                
                # Concatenar en lotes si hay muchos dataframes
                if len(dataframes) > 10:
                    batch_size = 5
                    combined_data = []
                    for i in range(0, len(dataframes), batch_size):
                        batch = dataframes[i:i+batch_size]
                        combined_data.append(pd.concat(batch, ignore_index=True))
                    full_data = pd.concat(combined_data, ignore_index=True)
                else:
                    full_data = pd.concat(dataframes, ignore_index=True)
                
                # Optimizar dataframe final
                full_data = optimize_dataframe(full_data)
                
                # Guardar en el estado de sesión
                st.session_state["filtered_data"] = full_data
                st.session_state["data_loaded"] = True
                
                # Limpiar y mostrar éxito
                progress_container.empty()
                st.success(f"Se cargaron {len(dataframes)} archivos correctamente. "
                          f"Total de registros: {len(full_data):,}")
                
                # Mostrar muestra de datos
                with st.expander("Vista previa de datos"):
                    st.dataframe(full_data.head(10), use_container_width=True)
                    
                    # Información útil sobre el conjunto de datos
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de jugadores", f"{full_data['Player'].nunique():,}")
                    with col2:
                        st.metric("Total de equipos", f"{full_data['Team within selected timeframe'].nunique():,}")
                    with col3:
                        st.metric("Temporadas", f"{full_data['Season'].nunique()}")
            else:
                progress_container.empty()
                st.warning("No se pudo cargar ningún archivo. Verifica la conexión o los filtros seleccionados.")

# [Aquí van todas las funciones de páginas originales]
def search_page():
    st.title("BUSCAR JUGADORES EN TODO EL MUNDO ⚽️")

    if "filtered_data" in st.session_state:
        data = st.session_state["filtered_data"]

        # Barra lateral para filtros
        st.sidebar.header("Filtros de Búsqueda")

        # Filtro de temporada
        selected_seasons = st.sidebar.multiselect(
            "Selecciona las temporadas:",
            options=sorted(data["Season"].dropna().unique().tolist()),
            default=sorted(data["Season"].dropna().unique().tolist()),
            key="season_filter"
        )

        # Filtrar datos según las temporadas seleccionadas
        filtered_data = data[data["Season"].isin(selected_seasons)]

        # Filtro de competición
        available_competitions = sorted(filtered_data["Competition"].dropna().unique().tolist())
        selected_competitions = st.sidebar.multiselect(
            "Selecciona las competiciones:",
            options=["Todos"] + available_competitions,
            default="Todos",
            key="competition_filter"
        )

        # Filtrar datos según las competiciones seleccionadas
        if "Todos" not in selected_competitions:
            filtered_data = filtered_data[filtered_data["Competition"].isin(selected_competitions)]

        # Filtro de equipo
        available_teams = sorted(filtered_data["Team within selected timeframe"].dropna().unique().tolist())
        selected_teams = st.sidebar.multiselect(
            "Selecciona los equipos:",
            options=["Todos"] + available_teams,
            default="Todos",
            key="team_filter"
        )

        # Filtrar datos según los equipos seleccionados
        if "Todos" not in selected_teams:
            filtered_data = filtered_data[filtered_data["Team within selected timeframe"].isin(selected_teams)]

        # Filtro de rango de edad
        min_age, max_age = filtered_data["Age"].min(), filtered_data["Age"].max()
        age_range = st.sidebar.slider(
            "Rango de edades:",
            int(min_age), int(max_age), (int(min_age), int(max_age)),
            key="age_filter"
        )

        # Filtrar datos según el rango de edad seleccionado
        filtered_data = filtered_data[
            (filtered_data["Age"] >= age_range[0]) &
            (filtered_data["Age"] <= age_range[1])
        ]

        # Filtros adicionales en la barra lateral
        st.sidebar.header("Filtros Adicionales")

        # Filtro de minutos jugados
        min_minutes, max_minutes = filtered_data["Minutes played"].min(), filtered_data["Minutes played"].max()
        minutes_range = st.sidebar.slider(
            "Rango de minutos jugados:",
            int(min_minutes), int(max_minutes), (int(min_minutes), int(max_minutes)),
            key="minutes_filter"
        )

        # Filtro de pierna dominante
        available_feet = sorted(filtered_data["Foot"].dropna().unique().tolist())
        selected_feet = st.sidebar.multiselect(
            "Pierna dominante:",
            options=["Todos"] + available_feet,
            default="Todos",
            key="foot_filter"
        )

        # Aplicar filtros finales
        filtered_data = filtered_data[
            (filtered_data["Minutes played"] >= minutes_range[0]) &
            (filtered_data["Minutes played"] <= minutes_range[1])
        ]
        if "Todos" not in selected_feet:
            filtered_data = filtered_data[filtered_data["Foot"].isin(selected_feet)]

        # Mostrar resultados
        if not filtered_data.empty:
            columns_to_display = [
                "Player", "Team within selected timeframe", "Age", "Foot",
                "Passport country", "Minutes played", "Season", "Competition"
            ]
            # Asegúrate de ajustar el número de filas que quieres mostrar. Puedes también controlar el tamaño de la tabla.
            st.dataframe(filtered_data[columns_to_display], use_container_width=True, height=700)  # Ajusta el valor de 'height' según lo necesites
        else:
            st.warning("No se encontraron jugadores que coincidan con los filtros seleccionados.")
    else:
        st.warning("Primero debes cargar los datos en la pestaña principal.")

def comparison_page():
    st.write("COMPARACIÓN DE JUGADORES ENTRE VARIAS TEMPORADAS ⚽️")

    if "filtered_data" not in st.session_state or st.session_state["filtered_data"].empty:
        st.warning("Primero debes cargar los datos en la pestaña principal.")
        return

    # Obtener los datos preprocesados
    data = st.session_state["filtered_data"].copy()

    # Crear una columna única `Player Instance` para diferenciar por temporada y equipo
    data["Player Instance"] = (
        data["Player"] + " | " +
        data["Team within selected timeframe"].fillna("Sin equipo") + " | " +
        data["Season"].astype(str)
    )

    # Selección múltiple de jugadores por instancia
    selected_instances = st.multiselect(
        "Selecciona jugadores para comparar:",
        options=sorted(data["Player Instance"].unique()),
        format_func=lambda instance: instance
    )

    if not selected_instances:
        st.warning("Por favor, selecciona al menos un jugador para comparar.")
        return

    # Filtrar los datos de las instancias seleccionadas
    players_to_compare = data[data["Player Instance"].isin(selected_instances)]

    # Filtro por posición para elegir métricas específicas
    selected_position = st.selectbox(
        "Selecciona la posición de los jugadores:",
        options=list(METRICS_BY_POSITION.keys())
    )

    # Filtrar las métricas específicas para la posición seleccionada
    metrics = METRICS_BY_POSITION[selected_position]
    available_metrics = [metric[0] for metric in metrics if metric[0] in players_to_compare.columns]
    metric_labels = {metric[0]: metric[1] for metric in metrics if metric[0] in players_to_compare.columns}

    # Mostrar métricas faltantes para depuración
    missing_metrics = [metric[0] for metric in metrics if metric[0] not in players_to_compare.columns]
    if missing_metrics:
        st.warning(f"Métricas faltantes para esta posición: {', '.join(missing_metrics)}")

    if not available_metrics:
        st.warning("No hay métricas disponibles para la posición seleccionada.")
        return

    # Filtrar y organizar los datos para comparación
    comparison_data = players_to_compare[["Player Instance"] + available_metrics].set_index("Player Instance")
    if comparison_data.empty:
        st.warning("No se encontraron datos para las métricas seleccionadas.")
        return

    # Renombrar columnas con etiquetas en español
    comparison_data.rename(columns=metric_labels, inplace=True)

    # Transponer la tabla para colocar métricas como filas
    comparison_data = comparison_data.T

    # Redondear valores a dos decimales
    comparison_data = comparison_data.round(2)

    # Resaltar el valor más alto en cada fila
    def highlight_max(s):
        """
        Resalta el valor más alto en una serie.
        """
        is_max = s == s.max()
        return ['background-color: lightgreen' if v else '' for v in is_max]

    # Aplicar estilo al DataFrame
    styled_comparison_data = comparison_data.style.apply(highlight_max, axis=1).format("{:.2f}")

    # Mostrar tabla en Streamlit
    st.write("### Comparación de métricas:")
    st.dataframe(styled_comparison_data, use_container_width=True)

def similarity_page():
    st.write("SIMILITUD DE JUGADORES (COSENO | EUCLIDIANA) ⚽️")

    if "filtered_data" in st.session_state and not st.session_state["filtered_data"].empty:
        data = st.session_state["filtered_data"]

        # Barra lateral para filtros
        st.sidebar.header("Filtros de Búsqueda")

        # Filtro de jugador de referencia
        player_to_compare = st.sidebar.selectbox(
            "Jugador de referencia:",
            options=sorted(data["Player"].dropna().unique().tolist())
        )

        # Filtro de posición
        selected_position = st.sidebar.selectbox(
            "Posición:",
            options=["Todos"] + list(METRICS_BY_POSITION.keys())
        )

        # Filtro de temporadas
        selected_seasons = st.sidebar.multiselect(
            "Temporadas:",
            options=sorted(data["Season"].dropna().unique().tolist()),
            default=sorted(data["Season"].dropna().unique().tolist())
        )

        # Filtro de competencias (actualizado dependiendo de las temporadas seleccionadas)
        # Filtrar las competiciones basadas en las temporadas seleccionadas
        available_competitions = data[data["Season"].isin(selected_seasons)]["Competition"].dropna().unique().tolist()
        selected_competitions = st.sidebar.multiselect(
            "Competencias:",
            options=["Todos"] + sorted(available_competitions),
            default="Todos"
        )

        # Filtro de país de pasaporte
        passport_country = st.sidebar.text_input("País de pasaporte (parcial o completo):", value="")

        # Filtros adicionales en la barra lateral
        min_age, max_age = int(data["Age"].min()), int(data["Age"].max())
        age_range = st.sidebar.slider("Rango de edades:", min_age, max_age, (min_age, max_age))

        min_minutes, max_minutes = int(data["Minutes played"].min()), int(data["Minutes played"].max())
        minutes_range = st.sidebar.slider("Rango de minutos jugados:", min_minutes, max_minutes, (min_minutes, max_minutes))

        dominant_foot = st.sidebar.multiselect(
            "Pierna dominante:",
            options=["Todos"] + sorted(data["Foot"].dropna().unique().tolist()),
            default="Todos"
        )

        # Filtrar datos
        filtered_data = data.copy()

        # Filtro por temporadas
        filtered_data = filtered_data[filtered_data["Season"].isin(selected_seasons)]

        # Filtro por competencias
        if "Todos" not in selected_competitions:
            filtered_data = filtered_data[filtered_data["Competition"].isin(selected_competitions)]

        # Filtro por posición
        if selected_position != "Todos":
            position_pattern = POSITION_PATTERNS.get(selected_position, "")
            if position_pattern:
                filtered_data = filtered_data[filtered_data["Primary position"].str.contains(position_pattern, na=False)]

        # Filtro por país de pasaporte
        if passport_country.strip():
            filtered_data = filtered_data[
                filtered_data["Passport country"].str.contains(passport_country, na=False, case=False)
            ]

        # Filtro por edad
        filtered_data = filtered_data[
            (filtered_data["Age"] >= age_range[0]) & (filtered_data["Age"] <= age_range[1])
        ]

        # Filtro por minutos jugados
        filtered_data = filtered_data[
            (filtered_data["Minutes played"] >= minutes_range[0]) & (filtered_data["Minutes played"] <= minutes_range[1])
        ]

        # Filtro por pierna dominante
        if "Todos" not in dominant_foot:
            filtered_data = filtered_data[filtered_data["Foot"].isin(dominant_foot)]

        # Obtener los datos del jugador seleccionado
        player_data = data[data["Player"] == player_to_compare]

        if player_data.empty:
            st.warning("No se encontraron datos para el jugador seleccionado.")
            return

        # Selección de temporada y equipo si hay múltiples registros
        if len(player_data) > 1:
            selected_row = st.selectbox(
                "Selecciona el equipo y la temporada:",
                options=player_data.index,
                format_func=lambda idx: f"{player_data.loc[idx, 'Team within selected timeframe']} - {player_data.loc[idx, 'Season']}"
            )
        else:
            selected_row = player_data.index[0]

        # Métricas por posición
        if selected_position != "Todos":
            metrics = METRICS_BY_POSITION[selected_position]
        else:
            metrics = [metric for position_metrics in METRICS_BY_POSITION.values() for metric in position_metrics]

        # Filtrar las métricas existentes
        available_metrics = [metric[0] for metric in metrics if metric[0] in filtered_data.columns]
        metric_labels = {metric[0]: metric[1] for metric in metrics if metric[0] in filtered_data.columns}

        # Normalización y cálculo de similitudes
        player_metrics = filtered_data[available_metrics].fillna(0)
        selected_player_metrics = player_data.loc[[selected_row], available_metrics].fillna(0)

        scaler = StandardScaler()
        player_metrics_normalized = scaler.fit_transform(player_metrics)
        selected_player_metrics_normalized = scaler.transform(selected_player_metrics)

        # Calcular similitudes
        cosine_similarities = cosine_similarity(selected_player_metrics_normalized, player_metrics_normalized).flatten()
        euclidean_dists = euclidean_distances(selected_player_metrics_normalized, player_metrics_normalized).flatten()
        max_distance = euclidean_dists.max()
        euclidean_similarities = (1 - (euclidean_dists / max_distance)) * 100

        # Añadir columnas de similitud
        filtered_data["Cosine Similarity"] = cosine_similarities * 100
        filtered_data["Euclidean Similarity"] = euclidean_similarities

        # Excluir al jugador seleccionado de los resultados
        similar_players = filtered_data[filtered_data.index != selected_row]

        # **Similitud Coseno**
        st.write("### Jugadores similares a {}".format(player_to_compare))
        st.write("""
        **Similitud Coseno:** Esta medida evalúa qué tan similares son dos jugadores en base a sus características, 
        como minutos jugados, edad, etc. Calcula el ángulo entre los vectores de características de los jugadores. 
        Mientras más alto es el valor, más similares son los jugadores.
        """)

        # Tabla de similitudes Coseno
        cosine_sorted = similar_players.sort_values(by="Cosine Similarity", ascending=False).head(30)
        cosine_table = cosine_sorted[
            ["Player", "Team within selected timeframe", "Season", "Competition", "Minutes played", "Age", "Passport country", "Cosine Similarity"]
        ]
        cosine_table = cosine_table.style.background_gradient(subset=["Cosine Similarity"], cmap="Greens", low=0, high=1)
        st.dataframe(cosine_table)

        # **Similitud Euclidiana**
        st.write("""
        **Similitud Euclidiana:** Esta medida evalúa la distancia entre dos jugadores en el espacio de características. 
        Mientras menor es la distancia, más similares son los jugadores. A medida que la distancia disminuye, 
        el valor de similitud se acerca a 100%.
        """)

        # Tabla de similitudes Euclidiana
        euclidean_sorted = similar_players.sort_values(by="Euclidean Similarity", ascending=False).head(30)
        euclidean_table = euclidean_sorted[
            ["Player", "Team within selected timeframe", "Season", "Competition", "Minutes played", "Age", "Passport country", "Euclidean Similarity"]
        ]
        euclidean_table = euclidean_table.style.background_gradient(subset=["Euclidean Similarity"], cmap="Blues", low=0, high=1)
        st.dataframe(euclidean_table)

    else:
        st.warning("Primero debes cargar los datos en la pestaña principal.")

def density_page():
    st.write("DENSIDAD DE JUGADORES EN BASE A MÉTRICAS ⚽️")

    if "filtered_data" in st.session_state:
        data = st.session_state["filtered_data"]

        # Mover los filtros a la barra lateral
        st.sidebar.write("### Filtros de Selección")

        # Filtro de temporada
        available_seasons = ["Todos"] + sorted(data["Season"].dropna().unique().tolist())
        selected_season = st.sidebar.selectbox("Selecciona la temporada:", options=available_seasons, index=0)

        # Filtro de competiciones basadas en la temporada
        filtered_data = data.copy()
        if selected_season != "Todos":
            filtered_data = filtered_data[filtered_data["Season"] == selected_season]

        available_competitions = ["Todos"] + sorted(filtered_data["Competition"].dropna().unique().tolist())
        selected_competition = st.sidebar.selectbox("Selecciona la competición:", options=available_competitions, index=0)

        if selected_competition != "Todos":
            filtered_data = filtered_data[filtered_data["Competition"] == selected_competition]

        # Filtro de equipos basados en la competición
        available_teams = ["Todos"] + sorted(filtered_data["Team within selected timeframe"].dropna().unique().tolist())
        selected_team = st.sidebar.selectbox("Selecciona el equipo:", options=available_teams, index=0)

        if selected_team != "Todos":
            filtered_data = filtered_data[filtered_data["Team within selected timeframe"] == selected_team]

        # Filtro de jugadores basado en el equipo seleccionado
        available_players = sorted(filtered_data["Player"].dropna().unique().tolist())
        if not available_players:
            st.warning("No hay jugadores disponibles para la selección actual.")
            return

        jugador_objetivo = st.sidebar.selectbox("Selecciona el primer jugador:", available_players, index=0)
        jugador_comparacion = st.sidebar.selectbox("Selecciona el jugador para comparar:", available_players, index=0)

        # Filtro de posición general
        posicion_general = st.sidebar.selectbox("Selecciona la posición general de los jugadores:", list(METRICS_BY_POSITION.keys()))

        # Obtener métricas basadas en la posición seleccionada
        metricas = METRICS_BY_POSITION[posicion_general]
        metric_names_english = [metric[0] for metric in metricas]
        metric_names_spanish = [metric[1] for metric in metricas]

        # Verificar si hay datos válidos
        if filtered_data.empty or len(metric_names_english) == 0:
            st.warning("No se encontraron datos válidos para generar gráficos.")
            return

        # Mostrar gráficos de densidad para cada métrica
        st.write("#### Gráficos de Densidad por Métrica")
        for metric_english, metric_spanish in zip(metric_names_english, metric_names_spanish):
            if metric_english not in filtered_data.columns:
                st.warning(f"La métrica '{metric_spanish}' no está disponible en los datos.")
                continue

            st.write(f"**Métrica:** {metric_spanish}")
            fig = generar_grafico_densidad(
                df=filtered_data,
                metric_english=metric_english,
                metric_spanish=metric_spanish,
                jugador_objetivo=jugador_objetivo,
                jugador_comparacion=jugador_comparacion,
                color_jugador_objetivo="#FF5733",
                color_jugador_comparacion="#33C4FF",
                promedio_liga=True
            )
            if fig:
                st.pyplot(fig)
    else:
        st.warning("Primero debes cargar los datos en la pestaña principal.")

def generar_grafico_densidad(df, metric_english, metric_spanish, jugador_objetivo, jugador_comparacion, color_jugador_objetivo, color_jugador_comparacion, promedio_liga=False):
    """
    Genera un gráfico de densidad para una métrica específica.
    """

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(15, 4))
    sns.kdeplot(data=df, x=metric_english, ax=ax, color="gray", fill=True, alpha=0.3, label="Todos los Jugadores")

    # Líneas para jugadores
    valor_objetivo = df.loc[df["Player"] == jugador_objetivo, metric_english].values
    valor_comparacion = df.loc[df["Player"] == jugador_comparacion, metric_english].values

    if len(valor_objetivo) > 0:
        ax.axvline(valor_objetivo[0], color=color_jugador_objetivo, linestyle="--", linewidth=2, label=jugador_objetivo)

    if len(valor_comparacion) > 0:
        ax.axvline(valor_comparacion[0], color=color_jugador_comparacion, linestyle="--", linewidth=2, label=jugador_comparacion)

    # Línea para el promedio de la liga (opcional)
    if promedio_liga:
        valor_promedio_liga = df[metric_english].mean()
        ax.axvline(valor_promedio_liga, color="blue", linestyle="--", linewidth=2, label="Promedio Liga")

    # Configuración del gráfico
    ax.set_title(f"Densidad: {metric_spanish}", fontsize=14)
    ax.set_xlabel(metric_spanish, fontsize=12)
    ax.set_ylabel("Densidad", fontsize=12)
    ax.legend(loc="upper right")

    plt.tight_layout()
    return fig

def create_scatter_plot():
    if 'filtered_data' not in st.session_state:
        return

    df = st.session_state['filtered_data']
    
    # Mover los filtros a la barra lateral
    with st.sidebar:
        seasons = ['Todas'] + list(df['Season'].unique())
        selected_season = st.selectbox('Temporada:', seasons)

    filtered_df = df if selected_season == 'Todas' else df[df['Season'] == selected_season].copy()
    
    with st.sidebar:
        competitions = ['Todas'] + list(filtered_df['Competition'].unique())
        selected_competition = st.selectbox('Competición:', competitions)
    
    if selected_competition != 'Todas':
        filtered_df = filtered_df[filtered_df['Competition'] == selected_competition]
    
    with st.sidebar:
        teams = list(filtered_df['Team within selected timeframe'].unique())
        selected_teams = st.multiselect('Equipos:', teams)
    
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Team within selected timeframe'].isin(selected_teams)]

    with st.sidebar:
        positions = list(POSITION_PATTERNS.keys())
        selected_positions = st.multiselect('Posiciones:', positions)
    
    with st.sidebar:
        nationalities = ['Todas'] + list(filtered_df['Passport country'].unique())
        selected_nationality = st.selectbox('Nacionalidad:', nationalities)
    
    with st.sidebar:
        feet = ['Todos'] + list(filtered_df['Foot'].unique())
        selected_foot = st.selectbox('Pie:', feet)

    min_minutes = int(filtered_df['Minutes played'].min())
    max_minutes = int(filtered_df['Minutes played'].max())
    
    with st.sidebar:
        selected_minutes = st.slider('Minutos jugados', min_minutes, max_minutes, min_minutes)
    
    filtered_df = filtered_df[filtered_df['Minutes played'] >= selected_minutes]

    if selected_nationality != 'Todas':
        filtered_df = filtered_df[filtered_df['Passport country'] == selected_nationality]
    
    if selected_foot != 'Todos':
        filtered_df = filtered_df[filtered_df['Foot'] == selected_foot]

    # Filtrar por posiciones seleccionadas
    if selected_positions:
        position_patterns = [POSITION_PATTERNS[pos] for pos in selected_positions]
        position_pattern = '|'.join(position_patterns)
        filtered_df = filtered_df[filtered_df['Primary position'].str.contains(position_pattern, na=False)]

    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()

    # Configuración del gráfico
    col7, col8, col9, col10 = st.columns(4)
    with col7:
        x_metric = st.selectbox('Eje X:', numeric_cols)
    with col8:
        y_metric = st.selectbox('Eje Y:', numeric_cols)
    with col9:
        size_metric = st.selectbox('Tamaño:', ['Minutes played'] + numeric_cols)
    with col10:
        color_options = ['Team within selected timeframe'] + numeric_cols
        color_metric = st.selectbox('Color:', color_options)

    if len(filtered_df) == 0:
        st.warning('No hay datos para mostrar con los filtros seleccionados.')
        return

    # Normalizar el tamaño y manejar NaN
    size_values = filtered_df[size_metric]
    size_values = size_values.fillna(size_values.mean())  # Reemplazar NaN con la media
    normalized_size = ((size_values - size_values.min()) / (size_values.max() - size_values.min()) * 30) + 10

    # Crear gráfico con estilo mejorado
    fig = px.scatter(
        filtered_df,
        x=x_metric,
        y=y_metric,
        size=normalized_size,
        color=color_metric,
        text='Player',
        hover_data=['Player', 'Team within selected timeframe'],
        title=f'{x_metric} vs {y_metric}',
        height=800,
        color_continuous_scale='Viridis'  # Puedes cambiar la paleta de colores
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='DarkSlateGray'),  # Bordes de los puntos
            opacity=0.8  # Opacidad para un mejor estilo visual
        ),
        textposition='top center',
        textfont=dict(size=12, family='Arial')  # Fuente mejorada
    )
    
    fig.update_layout(
        title_font=dict(size=18, family='Arial, sans-serif', color='rgb(0,0,0)'),
        showlegend=True,
        plot_bgcolor='white',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.02),
        margin=dict(l=50, r=150, t=50, b=50),
        xaxis=dict(showgrid=True, gridcolor='LightGray', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='LightGray', zeroline=False),
        font=dict(family='Arial, sans-serif', size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def radar_page():
    st.write("PERCENTILES ⚽️")

    if "filtered_data" in st.session_state and not st.session_state["filtered_data"].empty:
        data = st.session_state["filtered_data"]

        # Filtros de temporada y competición en la barra lateral
        seasons = data["Season"].unique()
        selected_season = st.sidebar.selectbox("Selecciona la temporada", seasons)

        competitions = data[data["Season"] == selected_season]["Competition"].unique()
        selected_competition = st.sidebar.selectbox("Selecciona la competición", ["Todos"] + list(competitions))

        if selected_competition == "Todos":
            filtered_data = data[data["Season"] == selected_season]
        else:
            filtered_data = data[(data["Season"] == selected_season) & (data["Competition"] == selected_competition)]

        # Seleccionar la posición en la barra lateral
        selected_position = st.sidebar.selectbox("Selecciona la posición", list(METRICS_BY_POSITION.keys()))

        # Filtrar los jugadores según la posición seleccionada
        position_pattern = POSITION_PATTERNS.get(selected_position, "")
        if position_pattern:
            filtered_data = filtered_data[filtered_data['Primary position'].str.contains(position_pattern, na=False)]
        
        # Agregar slider para minutos jugados en la barra lateral
        min_minutes = int(filtered_data['Minutes played'].min())
        max_minutes = int(filtered_data['Minutes played'].max())
        min_minutes_filter = st.sidebar.slider(
            "Filtrar por minutos jugados mínimos",
            min_value=min_minutes,
            max_value=max_minutes,
            value=350,
            step=50
        )

        # Filtrar jugadores según los minutos seleccionados
        filtered_data = filtered_data[filtered_data['Minutes played'] >= min_minutes_filter]
        total_players = len(filtered_data)

        if not filtered_data.empty:
            selected_player = st.selectbox("Selecciona un jugador", options=filtered_data["Player"].unique())
            jugador_data = filtered_data[filtered_data['Player'] == selected_player]

            if not jugador_data.empty:
                # Obtener todas las métricas disponibles para la posición
                all_metrics = METRICS_BY_POSITION[selected_position]
                
                # Crear un diccionario con las métricas agrupadas por categoría
                metrics_by_category = {}
                for metric in all_metrics:
                    if metric[2] not in metrics_by_category:
                        metrics_by_category[metric[2]] = []
                    metrics_by_category[metric[2]].append((metric[0], metric[1]))  # metric[1] es la descripción en español

                # Crear selectores de métricas en una fila
                st.write("### Selecciona las métricas a mostrar")
                
                # Crear columnas para cada categoría
                cols = st.columns(len(metrics_by_category))
                
                selected_metrics = []
                selected_categories = []
                metric_labels = {}  # Diccionario para mantener las etiquetas en español
                
                # Iterar sobre las categorías y crear los selectores en cada columna
                for col, (category, metrics) in zip(cols, metrics_by_category.items()):
                    with col:
                        st.write(f"**{category}**")
                        # Checkbox para seleccionar todas las métricas de la categoría
                        select_all = st.checkbox(f"Todas", key=f"select_all_{category}")
                        
                        # Métricas individuales
                        for metric_name, metric_desc in metrics:
                            if metric_name in filtered_data.columns:  # Solo mostrar métricas disponibles
                                selected = st.checkbox(
                                    f"{metric_desc}",  # Usar la descripción en español
                                    value=select_all,
                                    key=f"metric_{metric_name}"
                                )
                                if selected:
                                    selected_metrics.append(metric_name)
                                    selected_categories.append(category)
                                    metric_labels[metric_name] = metric_desc  # Guardar la etiqueta en español

                if selected_metrics:  # Solo crear el gráfico si hay métricas seleccionadas
                    # Convertir las métricas a tipo numérico
                    for param in selected_metrics:
                        filtered_data[param] = pd.to_numeric(filtered_data[param], errors='coerce').fillna(0)
                        jugador_data[param] = pd.to_numeric(jugador_data[param], errors='coerce').fillna(0)

                    # Calcular los percentiles
                    values = []
                    categories = []
                    for param in selected_metrics:
                        value = jugador_data[param].iloc[0]
                        percentile = stats.percentileofscore(filtered_data[param], value)
                        values.append(math.floor(percentile))
                        
                        # Buscar la categoría correspondiente
                        for metric in all_metrics:
                            if metric[0] == param:
                                categories.append(metric[2])
                                break

                    # Definir los colores para cada categoría
                    category_colors = CATEGORY_COLORS

                    # Asignar colores a las rebanadas según las categorías
                    slice_colors = [category_colors[cat] for cat in categories]

                    # Crear el gráfico de radar
                    baker = PyPizza(
                        params=[metric_labels[metric] for metric in selected_metrics],  # Usar etiquetas en español
                        background_color="#EBEBE9",
                        straight_line_color="#EBEBE9",
                        straight_line_lw=1,
                        last_circle_lw=0,
                        other_circle_lw=0,
                        inner_circle_size=18
                    )

                    fig, ax = baker.make_pizza(
                        values,
                        figsize=(8, 6.5),
                        color_blank_space="same",
                        slice_colors=slice_colors,
                        value_colors=["#F2F2F2"] * len(values),
                        value_bck_colors=slice_colors,
                        blank_alpha=0.4,
                        kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
                        kwargs_params=dict(color="#000000", fontsize=5, va="center"),
                        kwargs_values=dict(color="#000000", fontsize=7, zorder=3,
                                         bbox=dict(edgecolor="#000000", facecolor="cornflowerblue", 
                                                 boxstyle="round,pad=0.2", lw=1))
                    )

                    # Crear elementos de la leyenda
                    legend_elements = [
                        plt.Rectangle((0, 0), 1, 1, facecolor=color, label=category)
                        for category, color in category_colors.items()
                        if category in set(categories)  # Solo incluir categorías usadas
                    ]

                    # Agregar la leyenda
                    ax.legend(
                        handles=legend_elements,
                        loc='upper center',
                        bbox_to_anchor=(0.5, 1.1),
                        ncol=4,
                        frameon=False,
                        fontsize=10
                    )

                    # Ajustar el espaciado para acomodar la leyenda
                    plt.subplots_adjust(bottom=0.15)

                    # Agregar título y subtítulos
                    fig.text(0.5, 1.01, f"{selected_player} | {int(jugador_data['Age'].iloc[0])} años | {jugador_data['Team within selected timeframe'].iloc[0]}", 
                            size=16, ha="center", color="#000000")
                    fig.text(0.5, 0.98, f"{jugador_data['Foot'].iloc[0]} | {int(jugador_data['Minutes played'].iloc[0])} minutos | Comparado con {total_players} {selected_position}s", 
                            size=10, ha="center", color="#888888")
                    st.pyplot(fig)
                    
                else:
                    st.warning("Selecciona al menos una métrica para mostrar el gráfico.")
            else:
                st.warning("Jugador no encontrado.")
        else:
            st.warning("No hay jugadores que coincidan con los filtros seleccionados.")
    else:
        st.warning("Cargando los datos...")

def create_beeswarm_plot():
    # Utiliza los datos que ya tienes cargados en la sesión de Streamlit
    if "filtered_data" in st.session_state and not st.session_state["filtered_data"].empty:
        data = st.session_state["filtered_data"]
    else:
        st.warning("No se han cargado datos aún.")
        return

    # Convierte las columnas numéricas a tipo float
    numeric_columns = [col for col in data.columns if col in [metric[0] for metrics in METRICS_BY_POSITION.values() for metric in metrics]]
    data[numeric_columns] = data[numeric_columns].astype(float)

    # Pide al usuario que seleccione la temporada
    available_seasons = sorted(data["Season"].dropna().unique().tolist())
    selected_season = st.selectbox("Selecciona la temporada:", available_seasons, key="season_selectbox")

    # Filtra los datos por temporada seleccionada
    filtered_data = data[data["Season"] == selected_season]

    # Pide al usuario que seleccione la competición
    available_competitions = sorted(filtered_data["Competition"].dropna().unique().tolist())
    selected_competition = st.selectbox("Selecciona la competición:", available_competitions, key="competition_selectbox")

    # Filtra los datos por competición seleccionada
    filtered_data = filtered_data[filtered_data["Competition"] == selected_competition]

    # Pide al usuario que seleccione el equipo
    available_teams = sorted(filtered_data["Team within selected timeframe"].dropna().unique().tolist())
    available_teams.insert(0, "Todos")
    selected_team = st.selectbox("Selecciona el equipo:", available_teams, index=0, key="team_selectbox")

    # Filtra los datos por equipo seleccionado
    if selected_team != "Todos":
        filtered_data = filtered_data[filtered_data["Team within selected timeframe"] == selected_team]

    # Pide al usuario que seleccione la posición
    position_options = list(METRICS_BY_POSITION.keys())
    selected_position = st.selectbox("Selecciona la posición", position_options, key="position_selectbox")

    # Filtrar los datos por posición seleccionada
    position_pattern = POSITION_PATTERNS.get(selected_position, "")
    if position_pattern:
        filtered_data = filtered_data[filtered_data['Primary position'].str.contains(position_pattern, na=False)]

    # Pide al usuario que seleccione el jugador a destacar
    player_options = filtered_data['Player'].unique()
    selected_player = st.selectbox("Selecciona el jugador a destacar", player_options, key="player_selectbox")

    # Selecciona la métrica a visualizar
    if selected_position in METRICS_BY_POSITION:
        position_metrics = [metric[0] for metric in METRICS_BY_POSITION[selected_position]]
        selected_metric = st.selectbox("Selecciona la métrica a visualizar:", position_metrics, key="metric_selectbox")
    else:
        st.warning(f"No se encontraron métricas definidas para la posición '{selected_position}'.")
        return

    # Ajusta el código de visualización según la métrica seleccionada
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.set_facecolor('white')
    spines = ['top','bottom','left','right']
    for x in spines:
        if x in spines:
            ax.spines[x].set_visible(False)

    sns.swarmplot(x=selected_metric, data=filtered_data, zorder=1, ax=ax)

    if not filtered_data.empty and selected_player in filtered_data['Player'].values:
        valor = filtered_data[filtered_data['Player'] == selected_player][selected_metric].values[0]
    else:
        valor = 0

    ax.scatter(valor, 0, s=200, color='red', edgecolor='black', zorder=2)
    ax.set_xlabel(f'Valor de {selected_metric}', fontsize=12)
    ax.set_xticks([])
    ax.axvline(filtered_data[selected_metric].median(), lw=1.2, color='black')

    style = "Simple, tail_width=0.5, head_width=4, head_length=8"
    kw = dict(arrowstyle=style, color="k")
    a = patches.FancyArrowPatch((valor, 0), (valor+1, 0.2),
                                 connectionstyle="arc3,rad=.5", **kw)

    ax.add_patch(a)

    ax.text(valor+1.1, 0.2, selected_player.replace(' ', '\n'), fontsize=14, va='center')

    fig.text(.13, 1.05, f'Valor de {selected_metric} por jugador ({selected_position})', fontsize=15)
    fig.text(.13, 0.95, f'Jugadores de {selected_competition} en la temporada {selected_season} con más de\n270 min jugados', fontsize=15, color='grey')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    st.image(buf, use_column_width=True)

def create_radar_plot():
    if 'filtered_data' not in st.session_state:
        return

    df = st.session_state['filtered_data']
    
    # Normalizar los datos
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())

    # Mover los filtros a la barra lateral
    with st.sidebar:
        seasons = ['Todas'] + list(df['Season'].unique())
        selected_season = st.selectbox('Temporada:', seasons, key='radar_plot_season')

    filtered_df = df if selected_season == 'Todas' else df[df['Season'] == selected_season].copy()

    with st.sidebar:
        competitions = ['Todas'] + list(filtered_df['Competition'].unique())
        selected_competition = st.selectbox('Competición:', competitions, key='radar_plot_comp')

    if selected_competition != 'Todas':
        filtered_df = filtered_df[filtered_df['Competition'] == selected_competition]

    with st.sidebar:
        teams = list(filtered_df['Team within selected timeframe'].unique())
        selected_teams = st.multiselect('Equipos:', teams, key='radar_plot_teams')

    if selected_teams:
        filtered_df = filtered_df[filtered_df['Team within selected timeframe'].isin(selected_teams)]

    with st.sidebar:
        positions = ['Todas'] + list(POSITION_PATTERNS.keys())
        selected_position = st.selectbox('Posición:', positions, key='radar_plot_pos')

    if selected_position != 'Todas':
        position_pattern = POSITION_PATTERNS.get(selected_position, "")
        if position_pattern:
            filtered_df = filtered_df[filtered_df['Primary position'].str.contains(position_pattern, na=False)]

    with st.sidebar:
        min_minutes = int(filtered_df['Minutes played'].min())
        max_minutes = int(filtered_df['Minutes played'].max())
        if min_minutes == max_minutes:
            selected_minutes = min_minutes
        else:
            selected_minutes = st.slider('Minutos jugados:', int(min_minutes), int(max_minutes), int(min_minutes), key='radar_plot_minutes')
        filtered_df = filtered_df[filtered_df['Minutes played'] >= selected_minutes]

    with st.sidebar:
        players = list(filtered_df['Player'].unique())
        selected_players = st.multiselect('Jugadores (máx. 5):', players, max_selections=5, key='radar_plot_players')

    if selected_players:
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
        selected_metrics = st.multiselect('Métricas a comparar:', numeric_cols, default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols, key='radar_plot_metrics')

        if selected_metrics:
            df_radar = filtered_df[filtered_df['Player'].isin(selected_players)].copy()
            
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            angles = [n / float(len(selected_metrics)) * 2 * pi for n in range(len(selected_metrics))]
            angles += angles[:1]

            ax.set_theta_offset(pi / 2)
            ax.set_theta_direction(-1)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(selected_metrics, size=7)
            ax.tick_params(axis='x', which='major', pad=7)

            colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231']
            legend_handles = []
            for idx, player in enumerate(selected_players):
                values = df_radar[df_radar['Player'] == player][selected_metrics].values.flatten().tolist()
                values += values[:1]
                line, = ax.plot(angles, values, linewidth=2, linestyle='solid', color=colors[idx])
                ax.fill(angles, values, colors[idx], alpha=0.2)
                legend_handles.append(line)

            plt.legend(legend_handles, selected_players, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, fontsize=8)
            plt.subplots_adjust(top=0.85, bottom=0.15)
            plt.title('Comparación de métricas normalizadas de jugadores', fontsize=14, pad=20)
            st.pyplot(fig)

def scouting_report_page():
    st.title("📄 Generar Informe de Scouting con Gemini")

    if "filtered_data" in st.session_state:
        df = st.session_state["filtered_data"]

        # 🔹 Selección de temporada
        temporadas_disponibles = sorted(df["Season"].unique())
        temporada_seleccionada = st.selectbox("Selecciona la temporada:", temporadas_disponibles)

        # 🔹 Filtrar jugadores según la temporada seleccionada
        df_temporada = df[df["Season"] == temporada_seleccionada]

        # 🔹 Selección de jugador dentro de la temporada
        jugadores_disponibles = df_temporada["Player"].unique()
        jugador_seleccionado = st.selectbox("Selecciona un jugador:", jugadores_disponibles)

        # 🔹 Obtener información del jugador seleccionado
        jugador_info = df_temporada[df_temporada["Player"] == jugador_seleccionado].iloc[0]
        pais = jugador_info["Passport country"]
        posicion_original = jugador_info["Primary position"]
        partidos_jugados = jugador_info["Matches played"]
        minutos_jugados = jugador_info["Minutes played"]
        liga_jugador = jugador_info["Competition"]

        # 🔹 Filtrar jugadores de la misma liga y posición
        df_misma_posicion = df_temporada[
            (df_temporada["Competition"] == liga_jugador) & 
            (df_temporada["Primary position"] == posicion_original)
        ]

        # 🔹 Mapeo de posiciones para el diccionario `METRICS_BY_POSITION`
        position_mapping = {key: pos for pos, pattern in POSITION_PATTERNS.items() for key in pattern.split('|')}

        # Convertir la posición a la nomenclatura del diccionario `METRICS_BY_POSITION`
        posicion_jugador = "Desconocida"
        for pattern, position in position_mapping.items():
            if pattern in posicion_original:
                posicion_jugador = position
                break

        if posicion_jugador in METRICS_BY_POSITION:
            metricas_relevantes = [metrica[0] for metrica in METRICS_BY_POSITION[posicion_jugador]]
        else:
            metricas_relevantes = ["Matches played", "Minutes played"]

        # 🔹 Extraer estadísticas del jugador con métricas relevantes
        stats_jugador = {m: jugador_info[m] for m in metricas_relevantes if m in jugador_info}

        # 🔹 Calcular percentiles dentro de la liga
        percentiles = {}
        for metrica in metricas_relevantes:
            if metrica in df_misma_posicion.columns:
                valores = df_misma_posicion[metrica].dropna()
                if len(valores) > 0:
                    percentiles[metrica] = percentileofscore(valores, jugador_info[metrica])

        # 🔹 Separar métricas en "fuertes" y "débiles"
        sorted_stats = sorted(stats_jugador.items(), key=lambda x: percentiles.get(x[0], 50), reverse=True)
        mejores_metricas = dict(sorted_stats[:5])  # Top 5 métricas más fuertes
        metricas_a_mejorar = dict(sorted_stats[-5:])  # Bottom 5 métricas más débiles

        # 🔹 Función para conectar con Gemini
        def generar_reporte(jugador, pais, posicion, partidos, minutos, mejores, peores, percentiles):
            API_KEY = "AIzaSyCJKxie4DQqQCDnN_zhSmK_sbH4N7YeVeY"
            GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

            prompt = (
                f"Genera un informe de scouting para {jugador}, un jugador de {pais} que juega como {posicion}. "
                f"En la última temporada, jugó {partidos} partidos y acumuló {minutos} minutos. "
                f"Sus métricas más destacadas son: {mejores}. "
                f"Áreas a mejorar incluyen: {peores}. "
                f"Comparado con jugadores de la misma liga y posición, su percentil en cada métrica clave es: {percentiles}. "
                "Analiza su desempeño general y haz recomendaciones para su evolución como jugador."
            )

            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(GEMINI_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "⚠️ No se generó respuesta.")
                else:
                    return f"⚠️ Error {response.status_code}: {response.text}"
            except requests.exceptions.RequestException as e:
                return f"⚠️ Error en la conexión con Gemini: {e}"

        # 🔹 Botón para generar informe
        if st.button("🔍 Generar Informe"):
            resultado_gemini = generar_reporte(
                jugador_seleccionado, pais, posicion_jugador, partidos_jugados, minutos_jugados, mejores_metricas, metricas_a_mejorar, percentiles
            )
            st.write(resultado_gemini)

        # 🔹 Visualización de comparación con la liga
        st.subheader("📊 Comparación con jugadores de la misma liga y posición")
        fig, ax = plt.subplots(figsize=(8, 5))
        metricas_seleccionadas = list(mejores_metricas.keys()) + list(metricas_a_mejorar.keys())

        percentiles_valores = [percentiles.get(m, 50) for m in metricas_seleccionadas]

        ax.barh(metricas_seleccionadas, percentiles_valores, color=['green' if p > 50 else 'red' for p in percentiles_valores])
        ax.set_xlabel("Percentil en la Liga (0-100)")
        ax.set_title(f"Percentiles de {jugador_seleccionado} en su Liga")
        ax.axvline(x=50, color="gray", linestyle="--")  # Línea de referencia en el 50%
        st.pyplot(fig)

    else:
        st.warning("⚠️ Carga los datos primero desde la pestaña principal.")

# Sistema de navegación mejorado
def create_navigation():
    st.sidebar.title("Navegación")
    
    # Definir categorías de páginas
    categories = {
        "Datos": ["Cargar Datos 🏆", "Buscar 🔎"],
        "Análisis": ["Comparar ⚖️", "Similitud 🥇🥈🥉", "Densidad 📊"],
        "Visualizaciones": ["Dispersión - Análisis 📈", "Percentiles 🎯", "Besswarms ↔️", "Radar Comparativo ⚔️"],
        "Informes": ["Informe Scout911 📄"]
    }
    
    # Crear un acordeón por categoría
    selected_page = None
    
    # Primero, seleccionar categoría
    category_options = list(categories.keys())
    selected_category = st.sidebar.radio("Categorías", category_options)
    
    # Luego, mostrar páginas de la categoría seleccionada
    page_options = categories[selected_category]
    selected_page = st.sidebar.radio("Páginas", page_options)
    
    return selected_page

# Diccionario de funciones de páginas
tab_functions = {
    "Cargar Datos 🏆": main_page,
    "Buscar 🔎": search_page,
    "Comparar ⚖️": comparison_page,
    "Similitud 🥇🥈🥉": similarity_page,
    "Densidad 📊": density_page,
    "Dispersión - Análisis 📈": create_scatter_plot,
    "Percentiles 🎯": radar_page,
    "Besswarms ↔️": create_beeswarm_plot,
    "Radar Comparativo ⚔️": create_radar_plot,
    "Informe Scout911 📄": scouting_report_page,
}

# Función principal
def main():
    # Mostrar información de versión en la barra lateral
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"{APP_CONFIG.get('title', 'Deportivo Garcilaso ⚽️')}\n\n"
        f"Versión: {APP_CONFIG.get('version', '2.0.0')}\n"
        f"Desarrollado por: {APP_CONFIG.get('author', 'Deportivo Garcilaso')}\n"
        f"Última actualización: {APP_CONFIG.get('last_update', 'Marzo 2025')}"
    )
    
    # Navegación mejorada
    selected_tab = create_navigation()
    
    # Ejecutar la página seleccionada
    if selected_tab in tab_functions:
        tab_functions[selected_tab]()
    else:
        main_page()  # Página por defecto

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
