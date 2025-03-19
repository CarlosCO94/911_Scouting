import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
import re
from bs4 import BeautifulSoup
import pyarrow.parquet as pq
import os
from urllib.parse import urljoin

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Jugadores",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Aplicación de Análisis de Jugadores")

# Crear sesión para almacenar datos
if 'data' not in st.session_state:
    st.session_state['data'] = None

# Navegación en la barra lateral
st.sidebar.title("Navegación")
pagina = st.sidebar.radio(
    "Selecciona una página:",
    ["Cargar Datos", "Buscar Jugador", "Comparar Jugadores", 
     "Jugadores Similares", "Percentiles", "Generar Informe IA"]
)

# Funciones para cada página
def cargar_datos():
    st.header("Cargar Datos")
    
    # Opción para cargar archivo
    uploaded_file = st.file_uploader("Carga tu archivo de datos (CSV, Excel)", 
                                    type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Detectar tipo de archivo
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            # Guardar en la sesión
            st.session_state['data'] = data
            
            # Mostrar información del dataset
            st.success(f"¡Datos cargados correctamente! Filas: {data.shape[0]}, Columnas: {data.shape[1]}")
            
            # Mostrar primeras filas
            st.subheader("Vista previa de los datos")
            st.dataframe(data.head())
            
            # Información de columnas
            st.subheader("Información de columnas")
            buffer = []
            for column in data.columns:
                buffer.append({
                    "Columna": column,
                    "Tipo": str(data[column].dtype),
                    "Valores únicos": data[column].nunique(),
                    "Valores nulos": data[column].isna().sum()
                })
            st.table(pd.DataFrame(buffer))
            
        except Exception as e:
            st.error(f"Error al cargar los datos: {e}")

def buscar_jugador():
    st.header("Buscar Jugador")
    
    # Verificar si hay datos cargados
    if st.session_state['data'] is None:
        st.warning("Por favor, carga datos primero en la página 'Cargar Datos'")
        return
    
    data = st.session_state['data']
    
    # Determinar la columna de nombres de jugadores
    col_nombres = st.selectbox(
        "Selecciona la columna con los nombres de los jugadores:",
        data.columns.tolist()
    )
    
    # Crear campo de búsqueda
    busqueda = st.text_input("Buscar jugador por nombre:")
    
    if busqueda:
        # Filtrar jugadores que coincidan con la búsqueda
        resultados = data[data[col_nombres].str.contains(busqueda, case=False, na=False)]
        
        if len(resultados) > 0:
            st.success(f"Se encontraron {len(resultados)} jugadores")
            
            # Si hay muchos resultados, permitir seleccionar uno
            if len(resultados) > 1:
                nombres_jugadores = resultados[col_nombres].tolist()
                jugador_seleccionado = st.selectbox("Selecciona un jugador:", nombres_jugadores)
                ficha_jugador = resultados[resultados[col_nombres] == jugador_seleccionado]
            else:
                ficha_jugador = resultados
            
            # Mostrar información del jugador
            st.subheader(f"Ficha de {ficha_jugador[col_nombres].values[0]}")
            
            # Crear dos columnas para mostrar datos
            col1, col2 = st.columns(2)
            
            # Mostrar datos tabulares
            with col1:
                st.dataframe(ficha_jugador)
            
            # Mostrar gráfico de radar si hay suficientes columnas numéricas
            with col2:
                # Obtener columnas numéricas
                num_cols = ficha_jugador.select_dtypes(include=['float64', 'int64']).columns.tolist()
                
                if len(num_cols) >= 3:  # Necesitamos al menos 3 para un gráfico de radar
                    # Preparar datos para el gráfico de radar
                    categories = num_cols[:8]  # Limitamos a 8 para no saturar el gráfico
                    values = ficha_jugador[categories].values[0].tolist()
                    
                    # Crear figura
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                      r=values,
                      theta=categories,
                      fill='toself',
                      name=ficha_jugador[col_nombres].values[0]
                    ))
                    
                    fig.update_layout(
                      polar=dict(
                        radialaxis=dict(
                          visible=True,
                        )),
                      showlegend=True
                    )
                    
                    st.plotly_chart(fig)
                else:
                    st.info("No hay suficientes columnas numéricas para generar un gráfico de radar.")
            
        else:
            st.warning(f"No se encontraron jugadores con el nombre '{busqueda}'")

def comparar_jugadores():
    st.header("Comparar Jugadores")
    
    # Verificar si hay datos cargados
    if st.session_state['data'] is None:
        st.warning("Por favor, carga datos primero en la página 'Cargar Datos'")
        return
    
    data = st.session_state['data']
    
    # Determinar la columna de nombres de jugadores
    col_nombres = st.selectbox(
        "Selecciona la columna con los nombres de los jugadores:",
        data.columns.tolist()
    )
    
    # Seleccionar jugadores a comparar
    nombres_jugadores = data[col_nombres].unique().tolist()
    jugador1 = st.selectbox("Selecciona el primer jugador:", nombres_jugadores)
    jugador2 = st.selectbox("Selecciona el segundo jugador:", 
                           [j for j in nombres_jugadores if j != jugador1])
    
    # Obtener datos de ambos jugadores
    datos_j1 = data[data[col_nombres] == jugador1]
    datos_j2 = data[data[col_nombres] == jugador2]
    
    # Seleccionar métricas para comparar
    st.subheader("Selecciona métricas para comparar")
    # Obtener columnas numéricas
    num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    metricas = st.multiselect("Métricas a comparar:", num_cols)
    
    if metricas:
        # Mostrar comparación en gráfico de barras
        comp_data = pd.DataFrame({
            'Métrica': metricas,
            jugador1: [datos_j1[m].values[0] for m in metricas],
            jugador2: [datos_j2[m].values[0] for m in metricas]
        })
        
        # Convertir a formato largo para Plotly
        comp_long = pd.melt(comp_data, id_vars=['Métrica'], 
                           value_vars=[jugador1, jugador2],
                           var_name='Jugador', value_name='Valor')
        
        # Crear gráfico de barras
        fig = px.bar(comp_long, x='Métrica', y='Valor', color='Jugador',
                    barmode='group', title=f"Comparación entre {jugador1} y {jugador2}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar gráfico de radar
        if len(metricas) >= 3:
            # Normalizar valores para el radar chart
            radar_data = comp_data.copy()
            for m in metricas:
                max_val = max(radar_data[jugador1].max(), radar_data[jugador2].max())
                if max_val > 0:
                    radar_data[jugador1] = radar_data[jugador1] / max_val
                    radar_data[jugador2] = radar_data[jugador2] / max_val
            
            # Crear figura
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
              r=radar_data[jugador1],
              theta=radar_data['Métrica'],
              fill='toself',
              name=jugador1
            ))
            
            fig.add_trace(go.Scatterpolar(
              r=radar_data[jugador2],
              theta=radar_data['Métrica'],
              fill='toself',
              name=jugador2
            ))
            
            fig.update_layout(
              polar=dict(
                radialaxis=dict(
                  visible=True,
                  range=[0, 1]
                )),
              showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Mostrar tabla comparativa con diferencias
        st.subheader("Tabla comparativa")
        comp_table = pd.DataFrame({
            'Métrica': metricas,
            jugador1: [datos_j1[m].values[0] for m in metricas],
            jugador2: [datos_j2[m].values[0] for m in metricas],
            'Diferencia': [datos_j1[m].values[0] - datos_j2[m].values[0] for m in metricas],
            'Diferencia (%)': [((datos_j1[m].values[0] / datos_j2[m].values[0]) - 1) * 100 
                             if datos_j2[m].values[0] != 0 else float('inf') 
                             for m in metricas]
        })
        st.dataframe(comp_table)

def jugadores_similares():
    st.header("Encontrar Jugadores Similares")
    
    # Verificar si hay datos cargados
    if st.session_state['data'] is None:
        st.warning("Por favor, carga datos primero en la página 'Cargar Datos'")
        return
    
    data = st.session_state['data']
    
    # Determinar la columna de nombres de jugadores
    col_nombres = st.selectbox(
        "Selecciona la columna con los nombres de los jugadores:",
        data.columns.tolist()
    )
    
    # Seleccionar jugador de referencia
    nombres_jugadores = data[col_nombres].unique().tolist()
    jugador_ref = st.selectbox("Selecciona el jugador de referencia:", nombres_jugadores)
    
    # Seleccionar características para la comparación
    st.subheader("Selecciona características para encontrar similitud")
    # Obtener columnas numéricas
    num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    features = st.multiselect("Características a considerar:", num_cols)
    
    # Número de jugadores similares a mostrar
    num_similares = st.slider("Número de jugadores similares a mostrar:", 1, 10, 5)
    
    if features:
        try:
            # Crear copia de los datos para no modificar los originales
            similarity_data = data.copy()
            
            # Normalizar características
            scaler = StandardScaler()
            similarity_data[features] = scaler.fit_transform(similarity_data[features])
            
            # Obtener vector del jugador de referencia
            player_vector = similarity_data[similarity_data[col_nombres] == jugador_ref][features].values.reshape(1, -1)
            
            # Calcular similitud con todos los demás jugadores
            similarity_scores = []
            
            for idx, row in similarity_data.iterrows():
                if row[col_nombres] != jugador_ref:
                    vector = row[features].values.reshape(1, -1)
                    similarity = cosine_similarity(player_vector, vector)[0][0]
                    similarity_scores.append({
                        'Jugador': row[col_nombres],
                        'Similitud': similarity
                    })
            
            # Ordenar por similitud (mayor a menor)
            similarity_df = pd.DataFrame(similarity_scores).sort_values('Similitud', ascending=False)
            
            # Mostrar los jugadores más similares
            st.subheader(f"Jugadores más similares a {jugador_ref}")
            
            # Mostrar tabla de similitud
            similarity_df = similarity_df.head(num_similares).reset_index(drop=True)
            similarity_df.index = similarity_df.index + 1  # Empezar índice en 1
            st.table(similarity_df)
            
            # Visualizar la similitud
            fig = px.bar(similarity_df, x='Jugador', y='Similitud', 
                        title=f"Similitud con {jugador_ref}",
                        color='Similitud', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar comparación detallada con el jugador más similar
            if len(similarity_df) > 0:
                st.subheader(f"Comparación con el jugador más similar: {similarity_df['Jugador'].iloc[0]}")
                
                jugador_similar = similarity_df['Jugador'].iloc[0]
                
                # Obtener datos de ambos jugadores
                datos_ref = data[data[col_nombres] == jugador_ref]
                datos_sim = data[data[col_nombres] == jugador_similar]
                
                # Crear tabla comparativa
                comp_table = pd.DataFrame({
                    'Característica': features,
                    jugador_ref: [datos_ref[f].values[0] for f in features],
                    jugador_similar: [datos_sim[f].values[0] for f in features],
                    'Diferencia': [datos_ref[f].values[0] - datos_sim[f].values[0] for f in features],
                })
                st.dataframe(comp_table)
                
                # Crear gráfico de radar para visualizar similitud
                if len(features) >= 3:
                    # Normalizar valores para el radar chart
                    radar_data = comp_table.copy()
                    for f in features:
                        max_val = data[f].max()
                        if max_val > 0:
                            radar_data[jugador_ref] = radar_data[jugador_ref] / max_val
                            radar_data[jugador_similar] = radar_data[jugador_similar] / max_val
                    
                    # Crear figura
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                      r=radar_data[jugador_ref],
                      theta=radar_data['Característica'],
                      fill='toself',
                      name=jugador_ref
                    ))
                    
                    fig.add_trace(go.Scatterpolar(
                      r=radar_data[jugador_similar],
                      theta=radar_data['Característica'],
                      fill='toself',
                      name=jugador_similar
                    ))
                    
                    fig.update_layout(
                      polar=dict(
                        radialaxis=dict(
                          visible=True,
                          range=[0, 1]
                        )),
                      showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al calcular la similitud: {e}")

def percentiles():
    st.header("Análisis de Percentiles")
    
    # Verificar si hay datos cargados
    if st.session_state['data'] is None:
        st.warning("Por favor, carga datos primero en la página 'Cargar Datos'")
        return
    
    data = st.session_state['data']
    
    # Determinar la columna de nombres de jugadores
    col_nombres = st.selectbox(
        "Selecciona la columna con los nombres de los jugadores:",
        data.columns.tolist()
    )
    
    # Seleccionar jugador
    nombres_jugadores = data[col_nombres].unique().tolist()
    jugador = st.selectbox("Selecciona un jugador:", nombres_jugadores)
    
    # Seleccionar métricas para analizar
    st.subheader("Selecciona métricas para el análisis de percentiles")
    # Obtener columnas numéricas
    num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    metricas = st.multiselect("Métricas a analizar:", num_cols)
    
    if metricas:
        # Calcular percentiles
        percentiles_list = []
        
        for metrica in metricas:
            valor_jugador = data[data[col_nombres] == jugador][metrica].values[0]
            percentil = (data[metrica] <= valor_jugador).mean() * 100
            
            percentiles_list.append({
                'Métrica': metrica,
                'Valor': valor_jugador,
                'Percentil': percentil,
                'Color': 'green' if percentil >= 80 else ('yellow' if percentil >= 50 else 'red')
            })
        
        # Crear DataFrame de percentiles
        percentiles_df = pd.DataFrame(percentiles_list)
        
        # Mostrar tabla de percentiles
        st.subheader(f"Percentiles de {jugador}")
        st.dataframe(percentiles_df[['Métrica', 'Valor', 'Percentil']])
        
        # Visualizar percentiles
        fig = px.bar(percentiles_df, x='Métrica', y='Percentil', 
                    title=f"Percentiles de {jugador}",
                    color='Percentil', color_continuous_scale='RdYlGn',
                    labels={'Percentil': 'Percentil (%)'})
        
        # Añadir líneas de referencia
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=50,
            x1=len(metricas)-0.5,
            y1=50,
            line=dict(color="yellow", width=2, dash="dash"),
        )
        
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=80,
            x1=len(metricas)-0.5,
            y1=80,
            line=dict(color="green", width=2, dash="dash"),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Crear gráfico de dispersión para ver la distribución
        for metrica in metricas:
            st.subheader(f"Distribución de {metrica}")
            
            valor_jugador = data[data[col_nombres] == jugador][metrica].values[0]
            
            fig = px.histogram(data, x=metrica, nbins=30,
                              title=f"Distribución de {metrica}")
            
            # Añadir línea vertical para el jugador seleccionado
            fig.add_vline(x=valor_jugador, line_width=3, line_dash="dash", line_color="red",
                         annotation_text=f"{jugador}: {valor_jugador}", 
                         annotation_position="top right")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar estadísticas básicas
            st.write(f"Estadísticas de {metrica}:")
            stats = data[metrica].describe()
            st.write(f"- Media: {stats['mean']:.2f}")
            st.write(f"- Mediana: {stats['50%']:.2f}")
            st.write(f"- Desviación estándar: {stats['std']:.2f}")
            st.write(f"- Mínimo: {stats['min']:.2f}")
            st.write(f"- Máximo: {stats['max']:.2f}")

def generar_informe_ia():
    st.header("Generar Informe IA")
    
    # Verificar si hay datos cargados
    if st.session_state['data'] is None:
        st.warning("Por favor, carga datos primero en la página 'Cargar Datos'")
        return
    
    data = st.session_state['data']
    
    # Determinar la columna de nombres de jugadores
    col_nombres = st.selectbox(
        "Selecciona la columna con los nombres de los jugadores:",
        data.columns.tolist()
    )
    
    # Seleccionar jugador
    nombres_jugadores = data[col_nombres].unique().tolist()
    jugador = st.selectbox("Selecciona un jugador para el informe:", nombres_jugadores)
    
    # Botón para generar informe
    if st.button("Generar Informe IA"):
        st.info("Generando informe... Esto puede tomar unos momentos.")
        
        try:
            # Obtener datos del jugador
            datos_jugador = data[data[col_nombres] == jugador]
            
            # Obtener columnas numéricas para análisis
            num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            # Calcular percentiles para cada métrica
            percentiles = {}
            for col in num_cols:
                valor = datos_jugador[col].values[0]
                percentil = (data[col] <= valor).mean() * 100
                percentiles[col] = {
                    'valor': valor,
                    'percentil': percentil
                }
            
            # Identificar fortalezas (percentil > 80)
            fortalezas = [col for col, info in percentiles.items() if info['percentil'] >= 80]
            
            # Identificar debilidades (percentil < 20)
            debilidades = [col for col, info in percentiles.items() if info['percentil'] <= 20]
            
            # Encontrar jugadores similares
            # Normalizar datos
            similarity_data = data.copy()
            scaler = StandardScaler()
            similarity_data[num_cols] = scaler.fit_transform(similarity_data[num_cols])
            
            # Vector del jugador
            player_vector = similarity_data[similarity_data[col_nombres] == jugador][num_cols].values.reshape(1, -1)
            
            # Calcular similitud
            similarity_scores = []
            for idx, row in similarity_data.iterrows():
                if row[col_nombres] != jugador:
                    vector = row[num_cols].values.reshape(1, -1)
                    similarity = cosine_similarity(player_vector, vector)[0][0]
                    similarity_scores.append({
                        'Jugador': row[col_nombres],
                        'Similitud': similarity
                    })
            
            # Top 3 jugadores similares
            similares = pd.DataFrame(similarity_scores).sort_values('Similitud', ascending=False).head(3)
            
            # Generar informe
            st.subheader(f"Informe IA para {jugador}")
            
            st.markdown(f"""
            ## Resumen del jugador
            
            **{jugador}** presenta las siguientes características destacadas:
            
            ### Fortalezas
            """)
            
            if fortalezas:
                for f in fortalezas:
                    st.write(f"- **{f}**: {percentiles[f]['valor']:.2f} (Percentil {percentiles[f]['percentil']:.1f}%)")
            else:
                st.write("- No se identificaron fortalezas claras (métricas por encima del percentil 80)")
            
            st.markdown("### Áreas de mejora")
            
            if debilidades:
                for d in debilidades:
                    st.write(f"- **{d}**: {percentiles[d]['valor']:.2f} (Percentil {percentiles[d]['percentil']:.1f}%)")
            else:
                st.write("- No se identificaron debilidades claras (métricas por debajo del percentil 20)")
            
            st.markdown("### Perfil general")
            
            # Calcular percentil promedio
            promedio_percentil = sum([info['percentil'] for info in percentiles.values()]) / len(percentiles)
            
            if promedio_percentil >= 80:
                perfil = "élite"
            elif promedio_percentil >= 60:
                perfil = "destacado"
            elif promedio_percentil >= 40:
                perfil = "promedio"
            else:
                perfil = "en desarrollo"
            
            st.write(f"El jugador muestra un perfil **{perfil}** con un percentil promedio de {promedio_percentil:.1f}%.")
            
            st.markdown("### Jugadores similares")
            
            for idx, row in similares.iterrows():
                st.write(f"- **{row['Jugador']}** (Similitud: {row['Similitud']:.2f})")
            
            st.markdown("### Recomendaciones")
            
            if debilidades:
                st.write("Basado en las áreas de mejora identificadas, se recomienda:")
                for d in debilidades[:3]:  # Top 3 debilidades
                    st.write(f"- Desarrollar **{d}** mediante entrenamiento específico")
            
            st.markdown("### Conclusión")
            
            st.write(f"""
            {jugador} es un jugador con un perfil {perfil}. 
            {"Sus principales fortalezas están en " + ", ".join(fortalezas[:3]) + "." if fortalezas else "No presenta fortalezas claras en las métricas analizadas."} 
            {"Podría mejorar en " + ", ".join(debilidades[:3]) + "." if debilidades else "No presenta debilidades claras en las métricas analizadas."}
            """)
            
            # Visualización del perfil
            st.subheader("Perfil visual")
            
            # Crear gráfico de radar con las principales métricas
            top_metricas = sorted(percentiles.items(), key=lambda x: abs(x[1]['percentil'] - 50), reverse=True)[:8]
            
            categories = [m for m, _ in top_metricas]
            values = [percentiles[m]['percentil']/100 for m in categories]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
              r=values,
              theta=categories,
              fill='toself',
              name=jugador
            ))
            
            fig.update_layout(
              polar=dict(
                radialaxis=dict(
                  visible=True,
                  range=[0, 1]
                )),
              showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al generar el informe: {e}")

# Mostrar la página seleccionada
if pagina == "Cargar Datos":
    cargar_datos()
elif pagina == "Buscar Jugador":
    buscar_jugador()
elif pagina == "Comparar Jugadores":
    comparar_jugadores()
elif pagina == "Jugadores Similares":
    jugadores_similares()
elif pagina == "Percentiles":
    percentiles()
elif pagina == "Generar Informe IA":
    generar_informe_ia()
