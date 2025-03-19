import streamlit as st
import pandas as pd
from utils.data_loader import verificar_datos_cargados, obtener_datos
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

# Filtros para ayudar a encontrar jugadores para comparar
with st.expander("Filtros para selección de jugadores", expanded=False):
    # Filtro por posición si está disponible
    posicion_filtro = None
    if "Position" in data.columns:
        posiciones_unicas = sorted(data["Position"].unique().tolist())
        posiciones_agrupadas = ["Todas las posiciones"] + list(config.POSITION_GROUPS.keys())
        
        posicion_filtro = st.selectbox(
            "Filtrar por posición:",
            posiciones_agrupadas
        )
        
        # Filtrar jugadores por posición seleccionada
        if posicion_filtro != "Todas las posiciones":
            # Obtener todas las posiciones que pertenecen a este grupo
            posiciones_grupo = []
            for pos in posiciones_unicas:
                for p in config.POSITION_GROUPS[posicion_filtro]:
                    if p in pos:
                        posiciones_grupo.append(pos)
                        break
            
            data_filtrada = data[data["Position"].isin(posiciones_grupo)]
        else:
            data_filtrada = data
    else:
        data_filtrada = data
    
    # Filtro por equipo si está disponible
    if "Team" in data.columns:
        equipos = sorted(data_filtrada["Team"].unique().tolist())
        equipos = ["Todos los equipos"] + equipos
        
        equipo_filtro = st.selectbox(
            "Filtrar por equipo:",
            equipos
        )
        
        if equipo_filtro != "Todos los equipos":
            data_filtrada = data_filtrada[data_filtrada["Team"] == equipo_filtro]
    
    # Mostrar número de jugadores disponibles
    st.info(f"Jugadores disponibles: {len(data_filtrada)}")

# Seleccionar jugadores a comparar
nombres_jugadores = data_filtrada[col_nombres].unique().tolist()

col1, col2 = st.columns(2)
with col1:
    jugador1 = st.selectbox("Selecciona el primer jugador:", nombres_jugadores)
    
    # Mostrar información básica del primer jugador
    jugador1_info = data[data[col_nombres] == jugador1].iloc[0]
    
    # Crear tabla con información básica
    info_basica = []
    
    if "Team" in data.columns:
        info_basica.append(f"**Equipo:** {jugador1_info['Team']}")
    
    if "Position" in data.columns:
        info_basica.append(f"**Posición:** {jugador1_info['Position']}")
    
    if "Age" in data.columns:
        info_basica.append(f"**Edad:** {jugador1_info['Age']}")
    
    st.markdown(" | ".join(info_basica))

with col2:
    # Filtrar para no incluir al primer jugador
    jugador2 = st.selectbox("Selecciona el segundo jugador:", 
                           [j for j in nombres_jugadores if j != jugador1])
    
    # Mostrar información básica del segundo jugador
    jugador2_info = data[data[col_nombres] == jugador2].iloc[0]
    
    # Crear tabla con información básica
    info_basica = []
    
    if "Team" in data.columns:
        info_basica.append(f"**Equipo:** {jugador2_info['Team']}")
    
    if "Position" in data.columns:
        info_basica.append(f"**Posición:** {jugador2_info['Position']}")
    
    if "Age" in data.columns:
        info_basica.append(f"**Edad:** {jugador2_info['Age']}")
    
    st.markdown(" | ".join(info_basica))

# Determinar el tipo de jugadores para sugerir métricas apropiadas
posicion_j1 = None
posicion_j2 = None

if "Position" in data.columns:
    pos1 = data[data[col_nombres] == jugador1]["Position"].values[0]
    pos2 = data[data[col_nombres] == jugador2]["Position"].values[0]
    
    # Determinar grupo de posición para cada jugador
    for grupo, posiciones in config.POSITION_GROUPS.items():
        for p in posiciones:
            if p in pos1:
                posicion_j1 = grupo
            if p in pos2:
                posicion_j2 = grupo

# Crear pestañas para diferentes categorías de comparación
tabs = st.tabs(["General", "Ofensivo", "Defensivo", "Pases", "Personalizado"])

with tabs[0]:
    # Comparación general
    st.header(f"Comparación General: {jugador1} vs {jugador2}")
    
    # Obtener columnas numéricas
    num_cols = data.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    # Sugerir métricas generales
    metricas_sugeridas = [
        "Goals per 90", "Assists per 90", "xG per 90", "xA per 90", 
        "Shots per 90", "Key passes per 90", "Successful defensive actions per 90",
        "Passes per 90", "Accurate passes, %", "Progressive passes per 90"
    ]
    
    metricas_general = [col for col in metricas_sugeridas if col in num_cols]
    
    if metricas_general:
        # Generar la comparación
        comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas_general, col_nombres)
        
        # Mostrar comparación en gráfico de barras
        fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
        st.plotly_chart(fig_barras, use_container_width=True)
        
        # Mostrar gráfico de radar
        if len(metricas_general) >= 3:
            fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Mostrar tabla comparativa
        st.dataframe(comp_data)
    else:
        st.info("No hay suficientes métricas generales disponibles.")

with tabs[1]:
    # Comparación ofensiva
    st.header(f"Comparación Ofensiva: {jugador1} vs {jugador2}")
    
    # Sugerir métricas ofensivas
    metricas_sugeridas = [col for col in config.DEFAULT_COLUMNS["comparacion_ofensiva"] if col in num_cols]
    
    if metricas_sugeridas:
        # Opción para seleccionar métricas
        metricas_ofensivas = st.multiselect(
            "Selecciona métricas ofensivas:", 
            metricas_sugeridas,
            default=metricas_sugeridas[:min(5, len(metricas_sugeridas))]
        )
        
        if metricas_ofensivas:
            # Generar la comparación
            comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas_ofensivas, col_nombres)
            
            # Mostrar comparación en gráfico de barras
            fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
            st.plotly_chart(fig_barras, use_container_width=True)
            
            # Mostrar gráfico de radar
            if len(metricas_ofensivas) >= 3:
                fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Mostrar tabla comparativa
            st.dataframe(comp_data)
    else:
        st.info("No hay suficientes métricas ofensivas disponibles.")

with tabs[2]:
    # Comparación defensiva
    st.header(f"Comparación Defensiva: {jugador1} vs {jugador2}")
    
    # Sugerir métricas defensivas
    metricas_sugeridas = [col for col in config.DEFAULT_COLUMNS["comparacion_defensiva"] if col in num_cols]
    
    if metricas_sugeridas:
        # Opción para seleccionar métricas
        metricas_defensivas = st.multiselect(
            "Selecciona métricas defensivas:", 
            metricas_sugeridas,
            default=metricas_sugeridas[:min(5, len(metricas_sugeridas))]
        )
        
        if metricas_defensivas:
            # Generar la comparación
            comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas_defensivas, col_nombres)
            
            # Mostrar comparación en gráfico de barras
            fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
            st.plotly_chart(fig_barras, use_container_width=True)
            
            # Mostrar gráfico de radar
            if len(metricas_defensivas) >= 3:
                fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Mostrar tabla comparativa
            st.dataframe(comp_data)
    else:
        st.info("No hay suficientes métricas defensivas disponibles.")

with tabs[3]:
    # Comparación de pases
    st.header(f"Comparación de Pases: {jugador1} vs {jugador2}")
    
    # Sugerir métricas de pases
    metricas_sugeridas = [col for col in config.DEFAULT_COLUMNS["comparacion_pases"] if col in num_cols]
    
    if metricas_sugeridas:
        # Opción para seleccionar métricas
        metricas_pases = st.multiselect(
            "Selecciona métricas de pases:", 
            metricas_sugeridas,
            default=metricas_sugeridas[:min(5, len(metricas_sugeridas))]
        )
        
        if metricas_pases:
            # Generar la comparación
            comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas_pases, col_nombres)
            
            # Mostrar comparación en gráfico de barras
            fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
            st.plotly_chart(fig_barras, use_container_width=True)
            
            # Mostrar gráfico de radar
            if len(metricas_pases) >= 3:
                fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Mostrar tabla comparativa
            st.dataframe(comp_data)
    else:
        st.info("No hay suficientes métricas de pases disponibles.")

with tabs[4]:
    # Comparación personalizada
    st.header(f"Comparación Personalizada: {jugador1} vs {jugador2}")
    
    # Opción para seleccionar métricas personalizadas
    metricas = st.multiselect("Selecciona métricas a comparar:", num_cols)
    
    if metricas:
        # Generar la comparación
        comp_data = comparar_jugadores_datos(data, jugador1, jugador2, metricas, col_nombres)
        
        # Mostrar comparación en gráfico de barras
        fig_barras = grafico_comparacion_barras(comp_data, jugador1, jugador2)
        st.plotly_chart(fig_barras, use_container_width=True)
        
        # Mostrar gráfico de radar
        if len(metricas) >= 3:
            fig_radar = grafico_radar_comparacion(comp_data, jugador1, jugador2)
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Mostrar tabla comparativa
        st.dataframe(comp_data)
    else:
        st.info("Selecciona al menos una métrica para comparar a los jugadores.")

# Agregar análisis detallado de la comparación
if st.checkbox("Mostrar análisis detallado de las diferencias"):
    st.subheader("Análisis de Diferencias")
    
    # Seleccionar todas las métricas ya usadas en las pestañas
    todas_metricas = set()
    if 'metricas_general' in locals() and metricas_general:
        todas_metricas.update(metricas_general)
    if 'metricas_ofensivas' in locals() and metricas_ofensivas:
        todas_metricas.update(metricas_ofensivas)
    if 'metricas_defensivas' in locals() and metricas_defensivas:
        todas_metricas.update(metricas_defensivas)
    if 'metricas_pases' in locals() and metricas_pases:
        todas_metricas.update(metricas_pases)
    if 'metricas' in locals() and metricas:
        todas_metricas.update(metricas)
    
    todas_metricas = list(todas_metricas)
    
    if todas_metricas:
        # Generar la comparación completa
        comp_data_completa = comparar_jugadores_datos(data, jugador1, jugador2, todas_metricas, col_nombres)
        
        # Para cada métrica, determinar quién es mejor
        ventajas_j1 = []
        ventajas_j2 = []
        empates = []
        
        for idx, row in comp_data_completa.iterrows():
            metrica = row['Métrica']
            val1 = row[jugador1]
            val2 = row[jugador2]
            diff = row['Diferencia']
            diff_pct = row['Diferencia (%)']
            
            # Determinar si valores más altos son mejores (simplificación)
            higher_is_better = True  # Por defecto asumimos que valores más altos son mejores
            
            # Excepciones conocidas donde valores más bajos son mejores
            for lower_metric in ['Fouls', 'Yellow cards', 'Red cards']:
                if lower_metric in metrica:
                    higher_is_better = False
                    break
            
            # Determinar quién es mejor
            if higher_is_better:
                if val1 > val2:
                    ventajas_j1.append({
                        'Métrica': metrica,
                        'Diferencia': diff,
                        'Diferencia (%)': diff_pct if not pd.isna(diff_pct) and not pd.isinf(diff_pct) else "N/A"
                    })
                elif val2 > val1:
                    ventajas_j2.append({
                        'Métrica': metrica,
                        'Diferencia': -diff,
                        'Diferencia (%)': -diff_pct if not pd.isna(diff_pct) and not pd.isinf(diff_pct) else "N/A"
                    })
                else:
                    empates.append({
                        'Métrica': metrica,
                        'Valor': val1
                    })
            else:
                if val1 < val2:
                    ventajas_j1.append({
                        'Métrica': metrica,
                        'Diferencia': -diff,
                        'Diferencia (%)': -diff_pct if not pd.isna(diff_pct) and not pd.isinf(diff_pct) else "N/A"
                    })
                elif val2 < val1:
                    ventajas_j2.append({
                        'Métrica': metrica,
                        'Diferencia': diff,
                        'Diferencia (%)': diff_pct if not pd.isna(diff_pct) and not pd.isinf(diff_pct) else "N/A"
                    })
                else:
                    empates.append({
                        'Métrica': metrica,
                        'Valor': val1
                    })
        
        # Mostrar resultados
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"Ventajas de {jugador1}")
            if ventajas_j1:
                # Ordenar por diferencia porcentual
                ventajas_j1_df = pd.DataFrame(ventajas_j1)
                ventajas_j1_df = ventajas_j1_df.sort_values('Diferencia', ascending=False)
                st.dataframe(ventajas_j1_df)
            else:
                st.info(f"No se encontraron ventajas para {jugador1}")
        
        with col2:
            st.subheader(f"Ventajas de {jugador2}")
            if ventajas_j2:
                # Ordenar por diferencia porcentual
                ventajas_j2_df = pd.DataFrame(ventajas_j2)
                ventajas_j2_df = ventajas_j2_df.sort_values('Diferencia', ascending=False)
                st.dataframe(ventajas_j2_df)
            else:
                st.info(f"No se encontraron ventajas para {jugador2}")
        
        # Mostrar empates
        if empates:
            st.subheader("Métricas con valores iguales")
            st.dataframe(pd.DataFrame(empates))
        
        # Resumen de la comparación
        st.subheader("Resumen")
        
        total_metricas = len(ventajas_j1) + len(ventajas_j2) + len(empates)
        
        st.write(f"""
        - **{jugador1}** es mejor en **{len(ventajas_j1)}** métricas ({len(ventajas_j1)/total_metricas*100:.1f}%)
        - **{jugador2}** es mejor en **{len(ventajas_j2)}** métricas ({len(ventajas_j2)/total_metricas*100:.1f}%)
        - Ambos jugadores son iguales en **{len(empates)}** métricas ({len(empates)/total_metricas*100:.1f}%)
        """)
        
        # Métricas con mayores diferencias
        st.subheader("Mayores diferencias")
        
        # Combinar todas las ventajas
        todas_ventajas = []
        for v in ventajas_j1:
            todas_ventajas.append({
                'Jugador': jugador1,
                'Métrica': v['Métrica'],
                'Diferencia absoluta': abs(v['Diferencia'])
            })
        
        for v in ventajas_j2:
            todas_ventajas.append({
                'Jugador': jugador2,
                'Métrica': v['Métrica'],
                'Diferencia absoluta': abs(v['Diferencia'])
            })
        
        # Mostrar las 5 mayores diferencias
        if todas_ventajas:
            todas_ventajas_df = pd.DataFrame(todas_ventajas)
            top_diff = todas_ventajas_df.sort_values('Diferencia absoluta', ascending=False).head(5)
            st.dataframe(top_diff)
    else:
        st.info("Selecciona métricas en las pestañas anteriores para ver un análisis detallado.")
