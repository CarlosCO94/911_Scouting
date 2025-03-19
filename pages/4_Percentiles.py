import streamlit as st
import pandas as pd
from utils.data_laloader import verificar_datos_cargados, obtener_datos
from utils.data_processing import calcular_percentiles
from utils.visualization import grafico_percentiles_barras, grafico_distribucion_metrica
import config

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Percentiles",
    page_icon="📊",
    layout="wide"
)

# Título de la página
st.title("Análisis de Percentiles")

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

# Seleccionar jugador
nombres_jugadores = data[col_nombres].unique().tolist()
jugador = st.selectbox("Selecciona un jugador:", nombres_jugadores)

# Seleccionar métricas para analizar
st.subheader("Selecciona métricas para el análisis de percentiles")
# Obtener columnas numéricas
num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

# Sugerir métricas preconfiguradas si están disponibles
metricas_sugeridas = [col for col in config.DEFAULT_COLUMNS["percentiles_general"] if col in num_cols]
if len(metricas_sugeridas) > 0:
    metricas = st.multiselect(
        "Métricas a analizar:", 
        num_cols,
        default=metricas_sugeridas[:5]  # Seleccionar las primeras 5 métricas sugeridas por defecto
    )
else:
    metricas = st.multiselect("Métricas a analizar:", num_cols)

if metricas:
    # Calcular percentiles
    percentiles_df = calcular_percentiles(data, jugador, metricas, col_nombres)
    
    # Mostrar tabla de percentiles
    st.subheader(f"Percentiles de {jugador}")
    percentiles_styled = percentiles_df.copy()
    st.dataframe(percentiles_styled[['Métrica', 'Valor', 'Percentil']])
    
    # Visualizar percentiles
    fig = grafico_percentiles_barras(percentiles_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar resumen de percentiles
    st.subheader("Resumen de rendimiento")
    
    # Calcular promedio de percentiles
    promedio_percentil = percentiles_df['Percentil'].mean()
    
    # Determinar categoría del jugador
    categoria = "en desarrollo"
    for cat, umbral in sorted(config.PLAYER_CATEGORIES.items(), key=lambda x: x[1], reverse=True):
        if promedio_percentil >= umbral:
            categoria = cat
            break
    
    st.info(f"El percentil promedio de {jugador} es **{promedio_percentil:.1f}%**, lo que indica un perfil **{categoria}**.")
    
    # Mostrar fortalezas y debilidades
    fortalezas = percentiles_df[percentiles_df['Percentil'] >= 80]
    debilidades = percentiles_df[percentiles_df['Percentil'] <= 20]
    
    if not fortalezas.empty:
        st.success("### Fortalezas")
        for idx, row in fortalezas.iterrows():
            st.write(f"- **{row['Métrica']}**: {row['Valor']:.2f} (Percentil {row['Percentil']:.1f}%)")
    
    if not debilidades.empty:
        st.error("### Áreas de mejora")
        for idx, row in debilidades.iterrows():
            st.write(f"- **{row['Métrica']}**: {row['Valor']:.2f} (Percentil {row['Percentil']:.1f}%)")
    
    # Análisis detallado por métrica
    st.subheader("Análisis detallado por métrica")
    
    # Permitir al usuario seleccionar una métrica para un análisis más profundo
    metrica_detalle = st.selectbox("Selecciona una métrica para ver su distribución:", metricas)
    
    if metrica_detalle:
        # Obtener valor del jugador para la métrica seleccionada
        valor_jugador = data[data[col_nombres] == jugador][metrica_detalle].values[0]
        
        # Crear gráfico de distribución
        fig_dist = grafico_distribucion_metrica(data, metrica_detalle, valor_jugador, jugador)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Mostrar estadísticas básicas
        st.write(f"Estadísticas de {metrica_detalle}:")
        stats = data[metrica_detalle].describe()
        
        # Crear tabla de estadísticas
        stats_df = pd.DataFrame({
            'Estadística': ['Media', 'Mediana', 'Desv. Estándar', 'Mínimo', 'Máximo', 'Valor del jugador'],
            'Valor': [
                stats['mean'], 
                stats['50%'], 
                stats['std'], 
                stats['min'], 
                stats['max'],
                valor_jugador
            ]
        })
        
        st.table(stats_df)
        
        # Mostrar ranking
        ranking = (data[metrica_detalle] > valor_jugador).sum() + 1
        total = len(data)
        st.write(f"**Ranking**: {jugador} está en la posición **{ranking}** de **{total}** jugadores en {metrica_detalle}.")
else:
    st.info("Selecciona al menos una métrica para analizar los percentiles del jugador.")
