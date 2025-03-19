# Configuración general de la aplicación

# Información del repositorio de GitHub
GITHUB_REPO = "https://github.com/CarlosCO94/911_Scouting"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main"
PARQUET_DIR = "Ligas_Parquet"

# Columnas disponibles para cada tipo de análisis
DEFAULT_COLUMNS = {
    # Columna que contiene los nombres de los jugadores
    "nombres": "Player",
    
    # Columnas de identificación y contexto
    "info": [
        "Player", "Team", "Position", "Age", "Market value", 
        "Foot", "Height", "Weight", "Birth country"
    ],
    
    # Columnas para gráficos de radar ofensivos
    "radar_ofensivo": [
        "Goals per 90", "Assists per 90", "xG per 90", "xA per 90", 
        "Shots per 90", "Shots on target, %", "Dribbles per 90", 
        "Successful dribbles, %", "Progressive runs per 90"
    ],
    
    # Columnas para gráficos de radar defensivos
    "radar_defensivo": [
        "Defensive duels per 90", "Defensive duels won, %", 
        "Aerial duels per 90", "Aerial duels won, %", 
        "Interceptions per 90", "Shots blocked per 90", 
        "Successful defensive actions per 90", "Sliding tackles per 90"
    ],
    
    # Columnas para gráficos de radar de pases
    "radar_pases": [
        "Passes per 90", "Accurate passes, %", "Key passes per 90", 
        "Smart passes per 90", "Progressive passes per 90", 
        "Crosses per 90", "Through passes per 90", "xA per 90"
    ],
    
    # Columnas para gráficos de radar de porteros
    "radar_porteros": [
        "Save rate, %", "Shots against per 90", "Conceded goals per 90", 
        "xG against per 90", "Prevented goals per 90", "Exits per 90"
    ],
    
    # Columnas para comparación de jugadores ofensivos
    "comparacion_ofensiva": [
        "Goals per 90", "Non-penalty goals per 90", "xG per 90", 
        "Shots per 90", "Shots on target, %", "Goal conversion, %", 
        "Assists per 90", "xA per 90", "Dribbles per 90", 
        "Successful dribbles, %", "Touches in box per 90", 
        "Progressive runs per 90", "Accelerations per 90"
    ],
    
    # Columnas para comparación de jugadores defensivos
    "comparacion_defensiva": [
        "Successful defensive actions per 90", "Defensive duels per 90", 
        "Defensive duels won, %", "Aerial duels per 90", 
        "Aerial duels won, %", "Sliding tackles per 90", 
        "Shots blocked per 90", "Interceptions per 90", 
        "Fouls per 90", "Yellow cards per 90"
    ],
    
    # Columnas para comparación de pases/creación
    "comparacion_pases": [
        "Passes per 90", "Accurate passes, %", "Forward passes per 90", 
        "Accurate forward passes, %", "Long passes per 90", 
        "Accurate long passes, %", "xA per 90", "Shot assists per 90", 
        "Smart passes per 90", "Key passes per 90", 
        "Passes to final third per 90", "Passes to penalty area per 90", 
        "Deep completions per 90", "Progressive passes per 90"
    ],
    
    # Columnas para comparación de porteros
    "comparacion_porteros": [
        "Conceded goals per 90", "Shots against per 90", "Save rate, %", 
        "xG against per 90", "Prevented goals per 90", "Clean sheets", 
        "Exits per 90", "Aerial duels per 90"
    ],
    
    # Columnas para análisis de percentiles generales
    "percentiles_general": [
        "Goals per 90", "Assists per 90", "xG per 90", "xA per 90", 
        "Shots per 90", "Shots on target, %", "Dribbles per 90", 
        "Successful dribbles, %", "Successful defensive actions per 90", 
        "Defensive duels won, %", "Aerial duels won, %", 
        "Passes per 90", "Accurate passes, %", "Key passes per 90", 
        "Progressive passes per 90"
    ],
    
    # Columnas para análisis de percentiles ofensivos
    "percentiles_ofensivos": [
        "Goals per 90", "Non-penalty goals per 90", "xG per 90", 
        "Head goals per 90", "Shots per 90", "Shots on target, %", 
        "Goal conversion, %", "Touches in box per 90", 
        "Accelerations per 90", "Offensive duels per 90", 
        "Offensive duels won, %", "Progressive runs per 90"
    ],
    
    # Columnas para análisis de percentiles de pases/creación
    "percentiles_pases": [
        "Assists per 90", "xA per 90", "Shot assists per 90", 
        "Key passes per 90", "Smart passes per 90", 
        "Passes to final third per 90", "Passes to penalty area per 90", 
        "Through passes per 90", "Deep completions per 90", 
        "Deep completed crosses per 90", "Progressive passes per 90",
        "Crosses per 90", "Accurate crosses, %"
    ],
    
    # Columnas para análisis de percentiles defensivos
    "percentiles_defensivos": [
        "Successful defensive actions per 90", "Defensive duels per 90", 
        "Defensive duels won, %", "Aerial duels per 90", 
        "Aerial duels won, %", "Sliding tackles per 90", 
        "Shots blocked per 90", "Interceptions per 90"
    ],
    
    # Columnas para análisis de percentiles de porteros
    "percentiles_porteros": [
        "Save rate, %", "Clean sheets", "Conceded goals per 90", 
        "Shots against per 90", "xG against per 90", 
        "Prevented goals per 90", "Exits per 90"
    ]
}

# Colores para gráficos
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "tertiary": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd"
}

# Categorías de jugadores
PLAYER_CATEGORIES = {
    "élite": 80,
    "destacado": 60,
    "promedio": 40,
    "en desarrollo": 0
}

# Posiciones agrupadas para filtrado
POSITION_GROUPS = {
    "Porteros": ["GK", "Goalkeeper"],
    "Defensas": ["CB", "RB", "LB", "RWB", "LWB", "Defender"],
    "Centrocampistas": ["CM", "CDM", "CAM", "RM", "LM", "Midfielder"],
    "Atacantes": ["CF", "ST", "RW", "LW", "SS", "Forward", "Attacker"]
}

# Mappings de columnas por posición
POSITION_MAPPINGS = {
    "Porteros": {
        "radar": "radar_porteros",
        "comparacion": "comparacion_porteros",
        "percentiles": "percentiles_porteros"
    },
    "Defensas": {
        "radar": "radar_defensivo",
        "comparacion": "comparacion_defensiva",
        "percentiles": "percentiles_defensivos"
    },
    "Centrocampistas": {
        "radar": "radar_pases",
        "comparacion": "comparacion_pases",
        "percentiles": "percentiles_pases"
    },
    "Atacantes": {
        "radar": "radar_ofensivo",
        "comparacion": "comparacion_ofensiva",
        "percentiles": "percentiles_ofensivos"
    }
}
