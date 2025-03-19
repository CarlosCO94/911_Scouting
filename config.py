
# config.py
# Archivo de configuración centralizado para la aplicación de Deportivo Garcilaso

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
    # [resto de posiciones se mantiene igual...]
}

# URLs base por temporada
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

# Lista fallback de archivos por temporada (solo para referencia)
# En operación normal, se usará la función get_available_leagues() de league_detector.py
FILE_NAMES_FALLBACK = {
    "2025": [
        "Argentina Liga Profesional de Futbol 2025.parquet",
    ],
    "2024": [
        "Argentina Copa de la Liga 2024.parquet",
        "Peruvian Liga 1 2024.parquet",
        "Brasileirao 2024.parquet",
        "MLS 2024.parquet",
    ],
    # [otras temporadas...]
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
    "Matches played",
]

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
    "highlight": "#E74C3C",    # Rojo resaltado
    "background": "#F8F9FA",   # Fondo gris claro
    "text": "#333333",         # Texto gris oscuro
}

# Colores por categoría de métrica
CATEGORY_COLORS = {
    "General": CHART_COLORS["primary"],       # Azul
    "Defensa": CHART_COLORS["secondary"],     # Naranja
    "Pases": CHART_COLORS["tertiary"],        # Rojo
    "Ataque": CHART_COLORS["quaternary"]      # Verde
}

# Configuración de la aplicación
APP_CONFIG = {
    "title": "Deportivo Garcilaso ⚽️",
    "icon": "⚽🐈‍⬛🇵🇪📊",
    "layout": "wide",
    "theme": {
        "primaryColor": CHART_COLORS["primary"],
        "backgroundColor": CHART_COLORS["background"],
        "textColor": CHART_COLORS["text"],
    },
    "version": "2.0.0",
    "author": "Deportivo Garcilaso",
    "last_update": "Marzo 2025",
    "auto_detect_leagues": True  # Nueva opción para activar/desactivar detección automática
}
