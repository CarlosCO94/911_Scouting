import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from utils.data_laloader import verificar_datos_cargados, obtener_datos
from utils.data_processing import identificar_fortalezas_debilidades, encontrar_jugadores_similares
from utils.visualization import grafico_radar_perfil
import config

# Configuración de la página
st.set_page_config(
    page_title="Generar Informe IA",
    page_icon="🤖",
    layout="wide"
)

# Título de la página
st.title("Generar Informe IA")

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
jugador = st.selectbox("Selecciona un jugador para el informe:", nombres_jugadores)

# Botón para generar informe
if st.button("Generar Informe IA"):
    with st.spinner("Generando informe... Esto puede tomar unos momentos."):
        try:
            # Obtener datos del jugador
            datos_jugador = data[data[col_nombres] == jugador]
            
            # Obtener columnas numéricas para análisis
            num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            # Identificar fortalezas y debilidades
            analisis = identificar_fortalezas_debilidades(data, jugador, col_nombres, num_cols)
            fortalezas = analisis['fortalezas']
            debilidades = analisis['debilidades']
            percentiles = analisis['percentiles']
            promedio_percentil = analisis['promedio_percentil']
            
            # Encontrar jugadores similares
            similares = encontrar_jugadores_similares(data, jugador, num_cols, 3, col_nombres)
            
            # Determinar categoría del jugador
            categoria = "en desarrollo"
            for cat, umbral in sorted(config.PLAYER_CATEGORIES.items(), key=lambda x: x[1], reverse=True):
                if promedio_percentil >= umbral:
                    categoria = cat
                    break
            
            # Generar informe
            st.header(f"Informe IA para {jugador}")
            
            # Datos de contexto
            if 'liga_actual' in st.session_state and 'temporada_actual' in st.session_state:
                st.info(f"Liga: {st.session_state['liga_actual']} | Temporada: {st.session_state['temporada_actual']}")
            
            # Resumen del jugador
            st.subheader("Resumen del jugador")
            st.write(f"""
            **{jugador}** presenta un perfil **{categoria}** con un percentil promedio de {promedio_percentil:.1f}%.
            {"Sus fortalezas principales están en áreas ofensivas y de creación." if any(x in ' '.join(fortalezas) for x in ['Goal', 'Assist', 'xG', 'Attack', 'Shot', 'Pass']) else ""}
            {"Destaca en aspectos defensivos y de recuperación." if any(x in ' '.join(fortalezas) for x in ['Tackle', 'Intercept', 'Block', 'Recover', 'Aerial', 'Defen']) else ""}
            {"Muestra una gran capacidad técnica y control del balón." if any(x in ' '.join(fortalezas) for x in ['Dribble', 'Control', 'Touch', 'Technique', 'Carry']) else ""}
            """)
            
            # Mostrar fortalezas y debilidades en columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Fortalezas")
                if fortalezas:
                    for f in fortalezas:
                        st.write(f"- **{f}**: {percentiles[f]['valor']:.2f} (Percentil {percentiles[f]['percentil']:.1f}%)")
                else:
                    st.write("- No se identificaron fortalezas claras (métricas por encima del percentil 80)")
            
            with col2:
                st.subheader("Áreas de mejora")
                if debilidades:
                    for d in debilidades:
                        st.write(f"- **{d}**: {percentiles[d]['valor']:.2f} (Percentil {percentiles[d]['percentil']:.1f}%)")
                else:
                    st.write("- No se identificaron debilidades claras (métricas por debajo del percentil 20)")
            
            # Visualización del perfil
            st.subheader("Perfil visual")
            
            # Crear gráfico de radar con las principales métricas
            top_metricas = sorted(percentiles.items(), key=lambda x: abs(x[1]['percentil'] - 50), reverse=True)[:8]
            
            categories = [m for m, _ in top_metricas]
            values = [percentiles[m]['percentil']/100 for m in categories]
            
            fig = grafico_radar_perfil(categories, values, jugador)
            st.plotly_chart(fig, use_container_width=True)
            
            # Jugadores similares
            st.subheader("Jugadores similares")
            
            if not similares.empty:
                st.write("Los jugadores con un perfil más similar son:")
                for idx, row in similares.iterrows():
                    st.write(f"- **{row['Jugador']}** (Similitud: {row['Similitud']:.2f})")
            else:
                st.write("No se encontraron jugadores con perfiles similares.")
            
            # Recomendaciones
            st.subheader("Recomendaciones")
            
            if debilidades:
                st.write("Basado en las áreas de mejora identificadas, se recomienda:")
                for d in debilidades[:3]:  # Top 3 debilidades
                    st.write(f"- Desarrollar **{d}** mediante entrenamiento específico.")
                    
                    # Recomendaciones específicas según el tipo de métrica
                    if any(x in d for x in ['Goal', 'Finish', 'Shot', 'xG']):
                        st.write("  - Entrenar la definición con ejercicios de tiro a portería desde diferentes ángulos.")
                    elif any(x in d for x in ['Assist', 'Key', 'Pass', 'Cross', 'xA']):
                        st.write("  - Trabajar en la precisión de pases y ejercicios de visión periférica.")
                    elif any(x in d for x in ['Tackle', 'Intercept', 'Block', 'Defen']):
                        st.write("  - Mejorar posicionamiento defensivo y timing en las entradas.")
                    elif any(x in d for x in ['Dribble', 'Carry', 'Progress']):
                        st.write("  - Realizar ejercicios de control y conducción a alta velocidad.")
            
            # Conclusión
            st.subheader("Conclusión")
            
            st.write(f"""
            {jugador} es un jugador con un perfil {categoria}. 
            {"Sus principales fortalezas están en " + ", ".join(fortalezas[:3]) + "." if fortalezas else "No presenta fortalezas claras en las métricas analizadas."} 
            {"Podría mejorar en " + ", ".join(debilidades[:3]) + "." if debilidades else "No presenta debilidades claras en las métricas analizadas."}
            
            {"El jugador muestra un gran potencial y podría ser una excelente incorporación." if promedio_percentil >= 70 else ""}
            {"El jugador presenta un perfil equilibrado con margen de mejora." if 40 <= promedio_percentil < 70 else ""}
            {"El jugador necesita desarrollo en múltiples áreas para alcanzar un nivel competitivo." if promedio_percentil < 40 else ""}
            """)
            
            # Opción para exportar informe (placeholder)
            st.write("---")
            if st.button("Exportar Informe (PDF)"):
                st.info("Funcionalidad de exportación en desarrollo.")
            
        except Exception as e:
            st.error(f"Error al generar el informe: {e}")
else:
    st.info("Selecciona un jugador y haz clic en 'Generar Informe IA' para obtener un análisis detallado.")
