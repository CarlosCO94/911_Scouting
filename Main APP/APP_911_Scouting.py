import streamlit as st

# Configuración de la página en modo wide
st.set_page_config(page_title="911 Scouting", layout="wide")

# Título de la aplicación
st.title("911 Scouting")
st.subheader("By CECO")

# Definir las páginas
pg = st.navigation([
    st.Page("Pages/Busqueda_General.py", title="Búsqueda General", icon="🔍"),
    st.Page("Pages/Comparacion_Metricas.py", title="Comparación de Métricas", icon="📊"),
    st.Page("Pages/Porcentaje_Similitud.py", title="% de Similitud", icon="📈"),
    st.Page("Pages/Scoring.py", title="Scoring", icon="⭐"),
    st.Page("Pages/Smart_11.py", title="Smart 11", icon="⚽"),
])

# Ejecutar la página seleccionada
pg.run()
