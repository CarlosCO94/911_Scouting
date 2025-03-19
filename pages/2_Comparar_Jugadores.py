import streamlit as st
import pandas as pd
from utils.data_laloader import verificar_datos_cargados, obtener_datos
from utils.data_processing import comparar_jugadores_datos
from utils.visualization import grafico_comparacion_barras, grafico_radar_comparacion
import config

# Configuración de la página
st.set_page_config(
    page_title="Comparar Jugadores",
    page_icon="⚖️",
    layout="wide"
)

# Título de la página
st.title("Comparar Jugadores")

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

# Seleccionar jugadores a comparar
nombres_jugadores = data[col_nombres].unique().tolist()

col1, col2 = st.columns(2)
with col1:
    jugador1 = st.selectbox("Selecciona el primer jugador:", nombres_jugadores)

with col2:
    jugador2 = st.selectbox("Selecciona el segundo jugador:", 
                          [j for j in nombres_jugadores if j != jugador1])

# Seleccionar métricas para comparar
st.subheader("Selecciona métricas para comparar")
# Obtener columnas numéricas
num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Sugerir métricas preconfiguradas si están disponibles
metricas_sugeridas = [col for col in config.DEFAULT_COLUMNS["comparacion"] if col in num_cols]
if len(metricas_sugeridas) > 0:
    metricas = st.multiselect(
        "Métricas a comparar:", 
        num_cols,
        default=metricas_sugeridas[:5]  # Seleccionar las primeras 5 métricas sugeridas por defecto
    )
else:
    metricas = st.multiselect("Métricas a comparar:", num_cols)

if metricas:
    # Generar la comparación
    comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas, col_nombres)
    
    # Mostrar comparación en gráfico de barras
    st.subheader("Comparación de Métricas")
    fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
    st.plotly_chart(fig_barras, use_container_width=True)
    
    # Mostrar gráfico de radar
    if len(metricas) >= 3:
        st.subheader("Perfil Comparativo")
        fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Mostrar tabla comparativa con diferencias
    st.subheader("Tabla Comparativa")
    st.dataframe(comp_data)
    
    # Agregar análisis de fortalezas comparativas
    st.subheader("Análisis Comparativo")
    
    # Para cada métrica, determinar quién es mejor
    for idx, row in comp_data.iterrows():
        metrica = row['Métrica']
        val1 = row[jugador1]
        val2 = row[jugador2]
        diff = row['Diferencia']
        
        # Determinar si valores más altos son mejores (simplificación)
        higher_is_better = True  # Por defecto asumimos que valores más altos son mejores
        
        # Excepciones conocidas donde valores más bajos son mejores
        for lower_metric in ['Turnovers', 'Fouls', 'Yellow_Cards', 'Red_Cards']:
            if lower_metric in metrica:
                higher_is_better = False
                break
        
        # Determinar quién es mejor
        if higher_is_better:
            if val1 > val2:
                emoji = "🔼"
                mejor = jugador1
                peor = jugador2
                ventaja = diff
            elif val2 > val1:
                emoji = "🔽"
                mejor = jugador2
                peor = jugador1
                ventaja = -diff
            else:
                emoji = "🟰"
                mejor = None
                peor = None
                ventaja = 0
        else:
            if val1 < val2:
                emoji = "🔼"
                mejor = jugador1
                peor = jugador2
                ventaja = -diff
            elif val2 < val1:
                emoji = "🔽"
                mejor = jugador2
                peor = jugador1
                ventaja = diff
            else:
                emoji = "🟰"
                mejor = None
                peor = None
                ventaja = 0
        
        # Mostrar análisis solo si hay diferencia
        if mejor is not None:
            st.write(f"{emoji} **{metrica}**: {mejor} es mejor que {peor} por {abs(ventaja):.2f} unidades.")
else:
    st.info("Selecciona al menos una métrica para comparar a los jugadores.")
