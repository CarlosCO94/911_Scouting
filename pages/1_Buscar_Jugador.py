import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import verificar_datos_cargados, obtener_datos
from utils.visualization import grafico_radar_jugador
import config

# Configuración de la página
st.set_page_config(
    page_title="Buscar Jugador",
    page_icon="🔍",
    layout="wide"
)

# Título de la página
st.title("Buscar Jugador")

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

# Sidebar para filtros
st.sidebar.header("Filtros de búsqueda")

# Filtro por posición si está disponible
if "Position" in data.columns:
    posiciones_unicas = sorted(data["Position"].unique().tolist())
    
    # Agrupar posiciones
    posicion_grupos = {}
    for grupo, pos_list in config.POSITION_GROUPS.items():
        posicion_grupos[grupo] = [p for p in posiciones_unicas if any(pos in p for pos in pos_list)]
    
    # Flatten la lista de posiciones agrupadas
    posiciones_agrupadas = []
    for grupo, posiciones in posicion_grupos.items():
        if posiciones:  # Agregar solo si hay posiciones en este grupo
            posiciones_agrupadas.append(grupo)
            posiciones_agrupadas.extend([f"  {p}" for p in posiciones])
    
    # Opción para mostrar todas las posiciones
    posiciones_agrupadas = ["Todas las posiciones"] + posiciones_agrupadas
    
    filtro_posicion = st.sidebar.selectbox(
        "Filtrar por posición:",
        posiciones_agrupadas
    )
    
    # Filtrar jugadores por posición seleccionada
    if filtro_posicion != "Todas las posiciones":
        if filtro_posicion in config.POSITION_GROUPS.keys():
            # Si es un grupo, filtrar por todas las posiciones en ese grupo
            posiciones_filtro = []
            for pos in posiciones_unicas:
                if any(p in pos for p in config.POSITION_GROUPS[filtro_posicion]):
                    posiciones_filtro.append(pos)
            data_filtrada = data[data["Position"].isin(posiciones_filtro)]
        else:
            # Si es una posición específica (con espacios al inicio)
            posicion_limpia = filtro_posicion.strip()
            data_filtrada = data[data["Position"] == posicion_limpia]
    else:
        data_filtrada = data
else:
    data_filtrada = data

# Filtro por equipo si está disponible
if "Team" in data.columns:
    equipos = sorted(data_filtrada["Team"].unique().tolist())
    equipos = ["Todos los equipos"] + equipos
    
    filtro_equipo = st.sidebar.selectbox(
        "Filtrar por equipo:",
        equipos
    )
    
    if filtro_equipo != "Todos los equipos":
        data_filtrada = data_filtrada[data_filtrada["Team"] == filtro_equipo]

# Mostrar número de jugadores que cumplen los filtros
st.sidebar.info(f"Jugadores disponibles: {len(data_filtrada)}")

# Crear campo de búsqueda
busqueda = st.text_input("Buscar jugador por nombre:")

if busqueda:
    # Filtrar jugadores que coincidan con la búsqueda
    resultados = data_filtrada[data_filtrada[col_nombres].str.contains(busqueda, case=False, na=False)]
    
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
        jugador_nombre = ficha_jugador[col_nombres].values[0]
        st.header(f"{jugador_nombre}")
        
        # Información básica en tarjetas
        col1, col2, col3, col4 = st.columns(4)
        
        # Información de equipo si está disponible
        if "Team" in ficha_jugador.columns:
            with col1:
                st.info(f"**Equipo**: {ficha_jugador['Team'].values[0]}")
        
        # Información de posición si está disponible
        if "Position" in ficha_jugador.columns:
            with col2:
                st.info(f"**Posición**: {ficha_jugador['Position'].values[0]}")
        
        # Información de edad si está disponible
        if "Age" in ficha_jugador.columns:
            with col3:
                st.info(f"**Edad**: {ficha_jugador['Age'].values[0]}")
        
        # Información de valor de mercado si está disponible
        if "Market value" in ficha_jugador.columns:
            with col4:
                st.info(f"**Valor**: {ficha_jugador['Market value'].values[0]}")
        
        # Crear pestañas para mostrar diferentes tipos de información
        tabs = st.tabs(["Estadísticas", "Perfil ofensivo", "Perfil defensivo", "Pases"])
        
        with tabs[0]:
            # Estadísticas generales
            st.subheader("Estadísticas generales")
            
            # Seleccionar columnas importantes para mostrar
            cols_mostrar = []
            
            # Columnas de partidos y minutos
            if "Matches played" in ficha_jugador.columns:
                cols_mostrar.append("Matches played")
            if "Minutes played" in ficha_jugador.columns:
                cols_mostrar.append("Minutes played")
            
            # Columnas ofensivas básicas
            for col in ["Goals", "Assists", "xG", "xA"]:
                if col in ficha_jugador.columns:
                    cols_mostrar.append(col)
            
            # Columnas por 90 minutos
            for col in ["Goals per 90", "Assists per 90", "xG per 90", "xA per 90"]:
                if col in ficha_jugador.columns:
                    cols_mostrar.append(col)
            
            # Mostrar tabla con estas columnas
            if cols_mostrar:
                st.dataframe(ficha_jugador[cols_mostrar])
            else:
                st.dataframe(ficha_jugador)
        
        with tabs[1]:
            # Perfil ofensivo
            st.subheader("Perfil ofensivo")
            
            # Obtener columnas numéricas
            num_cols = ficha_jugador.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            # Columnas ofensivas para radar
            radar_cols = [col for col in config.DEFAULT_COLUMNS["radar_ofensivo"] if col in num_cols]
            
            if len(radar_cols) >= 3:
                # Crear gráfico de radar ofensivo
                fig = grafico_radar_jugador(ficha_jugador, jugador_nombre, radar_cols, col_nombres)
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar valores en una tabla
                tabla_ofensiva = pd.DataFrame({
                    'Métrica': radar_cols,
                    'Valor': [ficha_jugador[col].values[0] for col in radar_cols]
                })
                st.dataframe(tabla_ofensiva)
            else:
                st.info("No hay suficientes columnas ofensivas para generar un perfil.")
        
        with tabs[2]:
            # Perfil defensivo
            st.subheader("Perfil defensivo")
            
            # Columnas defensivas para radar
            radar_cols = [col for col in config.DEFAULT_COLUMNS["radar_defensivo"] if col in num_cols]
            
            if len(radar_cols) >= 3:
                # Crear gráfico de radar defensivo
                fig = grafico_radar_jugador(ficha_jugador, jugador_nombre, radar_cols, col_nombres)
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar valores en una tabla
                tabla_defensiva = pd.DataFrame({
                    'Métrica': radar_cols,
                    'Valor': [ficha_jugador[col].values[0] for col in radar_cols]
                })
                st.dataframe(tabla_defensiva)
            else:
                st.info("No hay suficientes columnas defensivas para generar un perfil.")
        
        with tabs[3]:
            # Perfil de pases
            st.subheader("Perfil de pases y creación")
            
            # Columnas de pases para radar
            radar_cols = [col for col in config.DEFAULT_COLUMNS["radar_pases"] if col in num_cols]
            
            if len(radar_cols) >= 3:
                # Crear gráfico de radar de pases
                fig = grafico_radar_jugador(ficha_jugador, jugador_nombre, radar_cols, col_nombres)
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar valores en una tabla
                tabla_pases = pd.DataFrame({
                    'Métrica': radar_cols,
                    'Valor': [ficha_jugador[col].values[0] for col in radar_cols]
                })
                st.dataframe(tabla_pases)
            else:
                st.info("No hay suficientes columnas de pases para generar un perfil.")
        
        # Mostrar todos los datos disponibles (expandible)
        with st.expander("Ver todos los datos disponibles"):
            st.dataframe(ficha_jugador)
    else:
        st.warning(f"No se encontraron jugadores con el nombre '{busqueda}'")
else:
    # Mostrar lista de jugadores si no hay búsqueda
    st.subheader("Lista de jugadores disponibles")
    
    # Limitar el número de jugadores mostrados para no sobrecargar la interfaz
    max_jugadores = min(100, len(data_filtrada))
    
    # Crear tabla con información básica
    cols_basicas = ["Player", "Team", "Position", "Age"]
    cols_basicas = [col for col in cols_basicas if col in data_filtrada.columns]
    
    if cols_basicas:
        st.dataframe(data_filtrada[cols_basicas].head(max_jugadores))
    else:
        st.dataframe(data_filtrada.head(max_jugadores))
    
    if len(data_filtrada) > max_jugadores:
        st.info(f"Mostrando {max_jugadores} de {len(data_filtrada)} jugadores. Usa la búsqueda para encontrar jugadores específicos.")
