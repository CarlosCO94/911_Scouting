
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import re
from io import BytesIO
import pandas as pd

@st.cache_data(ttl=3600*6)  # Cache por 6 horas
def detect_leagues_for_season(base_url, season):
    """
    Detecta automáticamente las ligas disponibles para una temporada específica.
    
    Args:
        base_url (str): URL base de la temporada
        season (str): Nombre de la temporada (por ejemplo, "2024")
        
    Returns:
        list: Lista de archivos .parquet disponibles
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
    
    # Si no encontramos nada, intentar una búsqueda más genérica
    if not available_files:
        try:
            # Intentar cargar un archivo con nombre genérico que podría contener la lista
            index_url = f"{base_url}/index.txt"
            response = requests.get(index_url, timeout=3)
            
            if response.status_code == 200:
                # Extraer archivos .parquet
                available_files = re.findall(r'([^\/\s]+\.parquet)', response.text)
        except:
            pass
    
    return sorted(available_files)

@st.cache_data(ttl=3600*24)  # Cache por 24 horas
def get_available_leagues():
    """
    Obtiene todas las ligas disponibles para todas las temporadas definidas.
    
    Returns:
        dict: Diccionario con temporadas como claves y listas de archivos como valores
    """
    from config import BASE_URLS, FILE_NAMES_FALLBACK
    
    # Usamos el fallback como base
    detected_file_names = FILE_NAMES_FALLBACK.copy()
    
    # Crear barra de progreso para la UI
    progress_placeholder = st.empty()
    progress_bar = None
    total_seasons = len(BASE_URLS)
    
    try:
        # Mostrar progreso solo si estamos en una sesión de Streamlit
        if st._is_running:
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

def validate_league_file(url):
    """
    Valida que un archivo de liga existe y tiene un formato correcto.
    
    Args:
        url (str): URL del archivo parquet
        
    Returns:
        bool: True si el archivo es válido, False si no
    """
    try:
        # Intenta obtener solo los primeros bytes del archivo
        headers = {'Range': 'bytes=0-1000'}
        response = requests.get(url, headers=headers, timeout=3)
        
        if response.status_code == 200 or response.status_code == 206:
            # Intenta leer el esquema del parquet (más rápido que leer todos los datos)
            try:
                file_bytes = BytesIO(response.content)
                # Leer solo metadatos
                pd.read_parquet(file_bytes, columns=[])
                return True
            except:
                return False
        return False
    except:
        return False
