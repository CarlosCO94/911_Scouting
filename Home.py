import streamlit as st
from utils.data_laloader import cargar_datos_github, cargar_datos_local

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Jugadores",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear sesión para almacenar datos si no existe
if 'data' not in st.session_state:
    st.session_state['data'] = None

# Título principal
st.title("Aplicación de Análisis de Jugadores")

# Descripción de la aplicación
st.markdown("""
Esta aplicación te permite analizar datos de jugadores de fútbol con múltiples herramientas:

- **Cargar Datos**: Carga datos desde GitHub o archivos locales
- **Buscar Jugador**: Encuentra y analiza jugadores individuales
- **Comparar Jugadores**: Compara estadísticas entre dos jugadores
- **Jugadores Similares**: Encuentra jugadores con perfiles similares
- **Percentiles**: Analiza el rendimiento de un jugador en percentiles
- **Generar Informe IA**: Crea informes detallados con análisis IA

Usa la barra lateral para navegar entre las diferentes páginas.
""")

# Separador
st.markdown("---")

# Sección de carga de datos
st.header("Cargar Datos")

# Opciones para cargar datos
opcion_carga = st.radio(
    "Selecciona una fuente de datos:",
    ["Cargar desde GitHub", "Cargar desde archivo local"]
)

if opcion_carga == "Cargar desde GitHub":
    cargar_datos_github()
else:
    cargar_datos_local()

# Información sobre datos cargados
if 'data' in st.session_state and st.session_state['data'] is not None:
    st.sidebar.success("✅ Datos cargados correctamente")
    
    # Mostrar información sobre los datos cargados
    if 'liga_actual' in st.session_state and 'temporada_actual' in st.session_state:
        st.sidebar.info(f"Liga: {st.session_state['liga_actual']}")
        st.sidebar.info(f"Temporada: {st.session_state['temporada_actual']}")
    elif 'fuente_datos' in st.session_state:
        st.sidebar.info(f"Archivo: {st.session_state['fuente_datos']}")
else:
    st.sidebar.warning("⚠️ No hay datos cargados")

# Información en el pie de página
st.markdown("---")
st.markdown("Desarrollado con Streamlit y Python")
