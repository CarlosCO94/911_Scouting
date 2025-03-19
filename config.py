# config.py
# Configuración para la aplicación de Deportivo Garcilaso

# URL base para todos los archivos
BASE_URL = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Ligas_Parquet"

# Las temporadas disponibles
SEASONS = [
    "2020", "2021", "2022", "2023", "2024", "2025", 
    "20-21", "21-22", "22-23", "23-24", "24-25"
]

# Crear URLs base para cada temporada
BASE_URLS = {season: f"{BASE_URL}/{season}" for season in SEASONS}

# Lista de archivo fallback (por si falla la detección automática)
FILE_NAMES_FALLBACK = {
    "2023": ["Peruvian Liga 1 2023.parquet"],
    "2024": ["Peruvian Liga 1 2024.parquet"]
}

# Columnas esenciales para cargar (optimización de memoria)
COMMON_COLUMNS = [
    "Player",
    "Team within selected timeframe",
    "Passport country",
    "Foot",
    "Age",
    "Minutes played",
    "Primary position",
    "Contract expires",
    "Position",
    "Matches played"
]

# Diccionario de métricas por posición
METRICS_BY_POSITION = {
    'Portero': [
        ("Matches played", "Partidos jugados", "General"),
        ("Minutes played", "Minutos jugados", "General"),
        ("Conceded goals per 90", "Goles concedidos por 90 minutos", "Defensa"),
        ("xG against per 90", "xG en contra por 90 minutos", "Defensa"),
        ("Prevented goals per 90", "Goles evitados por 90 minutos", "Defensa"),
        ("Save rate, %", "Tasa de paradas, %", "Defensa"),
        ("Exits per 90", "Salidas por 90 minutos", "Defensa"),
        ("Aerial duels per 90", "Duelos aéreos por 90 minutos", "Defensa"),
        ("Back passes received as GK per 90", "Pases atrás recibidos como portero por 90 minutos", "Pases"),
        ("Accurate passes, %", "Pases precisos, %", "Pases"),
        ("Accurate forward passes, %", "Pases precisos hacia adelante, %", "Pases"),
        ("Accurate long passes, %", "Pases largos precisos, %", "Pases")
    ],
    'Defensa': [
        ("Matches played", "Partidos jugados", "General"),
        ("Minutes played", "Minutos jugados", "General"),
        ("Aerial duels per 90", "Duelos aéreos por 90 minutos", "Defensa"),
        ("Aerial duels won, %", "Duelos aéreos ganados, %", "Defensa"),
        ("Defensive duels won, %", "Duelos defensivos ganados, %", "Defensa"),
        ("Duels won, %", "Duelos ganados, %", "Defensa"),
        ("Sliding tackles per 90", "Entradas deslizantes por 90 minutos", "Defensa"),
        ("Interceptions per 90", "Intercepciones por 90 minutos", "Defensa"),
        ("Key passes per 90", "Pases clave por 90 minutos", "Pases"),
        ("Short / medium passes per 90", "Pases cortos/medios por 90 minutos", "Pases"),
        ("Forward passes per 90", "Pases hacia adelante por 90 minutos", "Pases"),
        ("Long passes per 90", "Pases largos por 90 minutos", "Pases"),
        ("Passes per 90", "Pases por 90 minutos", "Pases"),
        ("Accurate passes to final third, %", "Pases precisos al tercio final, %", "Pases"),
        ("Accurate forward passes, %", "Pases precisos hacia adelante, %", "Pases"),
        ("Accurate back passes, %", "Pases precisos hacia atrás, %", "Pases"),
        ("Accurate long passes, %", "Pases largos precisos, %", "Pases"),
        ("Accurate passes, %", "Pases precisos, %", "Pases"),
        ("Accelerations per 90", "Aceleraciones por 90 minutos", "Ataque"),
        ("Progressive runs per 90", "Carreras progresivas por 90 minutos", "Ataque")
    ],
    'Lateral Izquierdo': [
        ("Matches played", "Partidos jugados", "General"),
        ("Minutes played", "Minutos jugados", "General"),
        ("Successful defensive actions per 90", "Acciones defensivas exitosas por 90 minutos", "Defensa"),
        ("Aerial duels won, %", "Duelos aéreos ganados, %", "Defensa"),
        ("Defensive duels won, %", "Duelos defensivos ganados, %", "Defensa"),
        ("Defensive duels per 90", "Duelos defensivos por 90 minutos", "Defensa"),
        ("Duels won, %", "Duelos ganados, %", "Defensa"),
        ("Interceptions per 90", "Intercepciones por 90 minutos", "Defensa"),
        ("Passes per 90", "Pases por 90 minutos", "Pases"),
        ("Forward passes per 90", "Pases hacia adelante por 90 minutos", "Pases"),
        ("Accurate passes to penalty area, %", "Pases precisos al área penal, %", "Pases"),
        ("Received passes per 90", "Pases recibidos por 90 minutos", "Pases"),
        ("Accurate passes to final third, %", "Pases precisos al tercio final, %", "Pases"),
        ("Accurate through passes, %", "Pases filtrados precisos, %", "Pases"),
        ("Accurate forward passes, %", "Pases precisos hacia adelante, %", "Pases"),
        ("Accurate progressive passes, %", "Pases progresivos precisos, %", "Pases"),
        ("xA per 90", "xA por 90 minutos", "Pases"),
        ("Successful attacking actions per 90", "Acciones ofensivas exitosas por 90 minutos", "Ataque"),
        ("Accelerations per 90", "Aceleraciones por 90 minutos", "Ataque"),
        ("Progressive runs per 90", "Carreras progresivas por 90 minutos", "Ataque"),
        ("Crosses to goalie box per 90", "Centros al área por 90 minutos", "Ataque"),
        ("Third assists per 90", "Terceras asistencias por 90 minutos", "Ataque")
    ],
    'Lateral Derecho': [
        ("Matches played", "Partidos jugados", "General"),
        ("Minutes played", "Minutos jugados", "General"),
        ("Successful defensive actions per 90", "Acciones defensivas exitosas por 90 minutos", "Defensa"),
        ("Aerial duels won, %", "Duelos aéreos ganados, %", "Defensa"),
        ("Defensive duels won, %", "Duelos defensivos ganados, %", "Defensa"),
        ("Defensive duels per 90", "Duelos defensivos por 90 minutos", "Defensa"),
        ("Duels won, %", "Duelos ganados, %", "Defensa"),
        ("Interceptions per 90", "Intercepciones por 90 minutos", "Defensa"),
        ("Passes per 90", "Pases por 90 minutos", "Pases"),
        ("Forward passes per 90", "Pases hacia adelante por 90 minutos", "Pases"),
        ("Accurate passes to penalty area, %", "Pases precisos al área penal, %", "Pases"),
        ("Received passes per 90", "Pases recibidos por 90 minutos", "Pases"),
        ("Accurate passes to final third, %", "Pases precisos al tercio final, %", "Pases"),
        ("Accurate through passes, %", "Pases filtrados precisos, %", "Pases"),
        ("Accurate forward passes, %", "Pases precisos hacia adelante, %", "Pases"),
        ("Accurate progressive passes, %", "Pases progresivos precisos, %", "Pases"),
        ("xA per 90", "xA por 90 minutos", "Pases"),
        ("Successful attacking actions per 90", "Acciones ofensivas exitosas por 90 minutos", "Ataque"),
        ("Accelerations per 90", "Aceleraciones por 90 minutos", "Ataque"),
        ("Progressive runs per 90", "Carreras progresivas por 90 minutos", "Ataque"),
        ("Crosses to goalie box per 90", "Centros al área por 90 minutos", "Ataque"),
        ("Third assists per 90", "Terceras asistencias por 90 minutos", "Ataque")
    ],
    # ... resto de posiciones ...
}

# Mapeo de posiciones para filtros
POSITION_PATTERNS = {
    'Portero': 'GK', 
    'Defensa': 'CB',
    'Lateral Izquierdo': 'LB|LWB', 
    'Lateral Derecho': 'RB|RWB',
    'Mediocampista Defensivo': 'DMF', 
    'Mediocampista Central': 'CMF',
    'Mediocampista Ofensivo': 'AMF', 
    'Extremos': 'RW|LW|LWF|RWF',
    'Delantero': 'CF'
}

# Colores para visualizaciones
CHART_COLORS = {
    "primary": "#1A78CF",      # Azul principal
    "secondary": "#FF9300",    # Naranja secundario
    "tertiary": "#FF6347",     # Rojo terciario
    "quaternary": "#32CD32",   # Verde cuaternario
}

# Colores por categoría de métrica
CATEGORY_COLORS = {
    "General": "#1A78CF",      # Azul
    "Defensa": "#FF9300",      # Naranja
    "Pases": "#FF6347",        # Rojo
    "Ataque": "#32CD32"        # Verde
}

# Configuración de la aplicación
APP_CONFIG = {
    "title": "Deportivo Garcilaso ⚽️",
    "icon": "⚽🐈‍⬛🇵🇪📊",
    "layout": "wide",
    "version": "2.0.0",
    "author": "Deportivo Garcilaso",
    "last_update": "Marzo 2025",
    "auto_detect_leagues": True
}
