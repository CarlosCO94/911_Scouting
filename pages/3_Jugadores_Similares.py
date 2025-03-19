import streamlit as st
import pandas as pd
from utils.data_loader import verificar_datos_cargados, obtener_datos
from utils.data_processing import encontrar_jugadores_similares, comparar_jugadores_datos
from utils.visualization import grafico_similitud_barras, grafico_radar_comparacion
import config

# Configuración de la página
st.set_page_config(
    page_title="Jugadores Similares",
    page_icon="👥",
    layout="wide"
)

# Título de la página
st.title("Encontrar Jugadores Similares")

# Verificar si hay datos cargados
if not verificar_datos_cargados():
    st.stop()

# Obtener datos
data = obtener_datos()

# Determinar la columna de nombres de jugadores
col_nombres = st.selectbox(
    "Selecciona la columna con los nombres de los jugadores:",
    data.columns.tolist(),
    index=data.columns.get_loc(config.DEFAULT_COLUMNS["nombres"]) if config.DEFAULT_COLUMNS["nombres"] in data.columns else 0
)

# Seleccionar jugador de referencia
nombres_jugadores = data[col_nombres].unique().tolist()
jugador_ref = st.selectbox("Selecciona el jugador de referencia:", nombres_jugadores)

# Seleccionar características para la comparación
st.subheader("Selecciona características para encontrar similitud")
# Obtener columnas numéricas
num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Sugerir métricas preconfiguradas si están disponibles
features_sugeridas = [col for col in config.DEFAULT_COLUMNS["comparacion_ofensiva"] if col in num_cols]
if len(features_sugeridas) > 0:
    features = st.multiselect(
        "Características a considerar:", 
        num_cols,
        default=features_sugeridas[:5]  # Seleccionar las primeras 5 métricas sugeridas por defecto
    )
else:
    features = st.multiselect("Características a considerar:", num_cols)

# Número de jugadores similares a mostrar
num_similares = st.slider("Número de jugadores similares a mostrar:", 1, 10, 5)

if features:
    try:
        # Encontrar jugadores similares
        similarity_df = encontrar_jugadores_similares(data, jugador_ref, features, num_similares, col_nombres)
        
        if not similarity_df.empty:
            # Mostrar los jugadores más similares
            st.subheader(f"Jugadores más similares a {jugador_ref}")
            
            # Mostrar tabla de similitud
            similarity_df.index = similarity_df.index + 1  # Empezar índice en 1
            st.table(similarity_df)
            
            # Visualizar la similitud
            fig = grafico_similitud_barras(similarity_df, jugador_ref)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar comparación detallada con el jugador más similar
            if len(similarity_df) > 0:
                st.subheader(f"Comparación con el jugador más similar: {similarity_df['Jugador'].iloc[0]}")
                
                jugador_similar = similarity_df['Jugador'].iloc[0]
                
                # Crear tabla comparativa
                comp_data = comparar_jugadores_datos(data, jugador_ref, jugador_similar, features, col_nombres)
                
                # Mostrar tabla
                st.dataframe(comp_data)
                
                # Crear gráfico de radar para visualizar similitud
                if len(features) >= 3:
                    st.subheader("Perfil comparativo")
                    fig_radar = grafico_radar_comparacion(comp_data, jugador_ref, jugador_similar)
                    st.plotly_chart(fig_radar, use_container_width=True)
                
                # Opción para ver detalles de otros jugadores similares
                if len(similarity_df) > 1:
                    st.subheader("Comparar con otros jugadores similares")
                    otro_similar = st.selectbox(
                        "Selecciona otro jugador para comparar:", 
                        similarity_df['Jugador'].iloc[1:].tolist()
                    )
                    
                    if st.button(f"Comparar con {otro_similar}"):
                        # Crear tabla comparativa
                        comp_data_alt = comparar_jugadores_datos(data, jugador_ref, otro_similar, features, col_nombres)
                        
                        # Mostrar tabla
                        st.dataframe(comp_data_alt)
                        
                        # Crear gráfico de radar
                        if len(features) >= 3:
                            fig_radar_alt = grafico_radar_comparacion(comp_data_alt, jugador_ref, otro_similar)
                            st.plotly_chart(fig_radar_alt, use_container_width=True)
        else:
            st.warning(f"No se encontraron jugadores similares a {jugador_ref}.")
            
    except Exception as e:
        st.error(f"Error al calcular la similitud: {e}")
else:
    st.info("Selecciona al menos una característica para encontrar jugadores similares.")
