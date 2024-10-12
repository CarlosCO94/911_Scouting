import streamlit as st
import pandas as pd
import requests
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Diccionario de métricas por posición (mantenido del código original)
metricas_por_posicion = {
    'Portero': ["Minutes played", "Conceded goals per 90", "Shots against per 90", "Clean sheets", "Save rate, %", 
                "xG against per 90", "Prevented goals per 90", "Back passes received as GK per 90", 
                "Exits per 90", "Aerial duels per 90"],
    'Centrales': ["Minutes played", "Defensive actions per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Sliding tackles per 90", "Possession won after a tackle", "Shots blocked per 90", 
                  "Interceptions per 90", "Forward passes per 90", "Through passes per 90", "Head goals"],
    'Laterales': ["Minutes played", "Assists per 90", "Duels per 90", "Defensive duels per 90", "Aerial duels per 90", 
                  "Shots blocked per 90", "Interceptions per 90", "Goals per 90", "Shots per 90", 
                  "Crosses per 90", "Dribbles per 90", "Offensive duels per 90", "Forward passes per 90"],
    'Volantes Centrales + MCO': ["Minutes played", "Goals", "Assists per 90", "Duels won, %", "Successful defensive actions per 90", 
                                 "Defensive duels per 90", "Long passes per 90", "Aerial duels per 90", 
                                 "Interceptions per 90", "Forward passes per 90", "Through passes per 90"],
    'Delantero + Extremos': ["Minutes played", "Goals per 90", "Assists per 90", "Shots per 90", "Shots on target, %", 
                             "Successful dribbles per 90", "Offensive duels per 90", "Received passes per 90", 
                             "Crosses per 90", "Dribbles per 90", "Accurate passes, %", "Forward passes per 90", 
                             "Through passes per 90"]
}

# URLs y configuraciones (mantenidas del código original)
league_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Ligas_Wyscout.csv"
base_raw_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"
api_url = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Funciones de carga de datos (mantenidas del código original)
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Cargar la información de las ligas
league_data = cargar_datos_csv(league_url)

# Obtener la lista de archivos CSV en la carpeta "Main APP" del repositorio
file_urls = []
try:
    response = requests.get(api_url)
    if response.status_code == 200:
        archivos = response.json()
        file_urls = [base_raw_url + file['name'] for file in archivos if file['name'].endswith('.csv')]
        file_names = [file['name'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Cargar datos de los jugadores
data_frames = []
if file_urls:
    for url, name in zip(file_urls, file_names):
        df = cargar_datos_csv(url)
        if not df.empty:
            match = re.search(r'(\d{4}(?:-\d{2,4})?)', name)
            if match:
                season = match.group(1)
                df['Season'] = season
            else:
                df['Season'] = 'Desconocida'

            if 'Competition' in df.columns:
                df['Competition'] = df['Competition']
            else:
                df['Competition'] = 'Unknown'

            data_frames.append(df)

# Combinar todos los dataframes si hay más de uno
if data_frames:
    combined_data = pd.concat(data_frames, ignore_index=True)

# Verificar columnas requeridas
required_columns = ['Full name', 'Team logo']
missing_columns = [col for col in required_columns if col not in combined_data.columns]
if missing_columns:
    st.error(f"Las siguientes columnas necesarias no están presentes en los datos: {', '.join(missing_columns)}")
else:
    # Nuevas funciones para mejorar la visualización
    def generate_radar_chart(player_data, metrics, player_name):
        num_vars = len(metrics)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        
        values = player_data[metrics].values.flatten().tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_title(f"Radar Chart - {player_name}")
        
        for angle, value, metric in zip(angles[:-1], values[:-1], metrics):
            ax.text(angle, value, f'{value:.2f}', ha='center', va='center')

        return fig

    def generate_scatter_plot(data, x_metric, y_metric, highlight_player=None):
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.scatterplot(data=data, x=x_metric, y=y_metric, ax=ax)
        
        if highlight_player:
            player_data = data[data['Full name'] == highlight_player]
            ax.scatter(player_data[x_metric], player_data[y_metric], color='red', s=100, label=highlight_player)
        
        ax.set_title(f'{x_metric} vs {y_metric}')
        ax.legend()
        return fig

    # Crear pestañas para organizar la interfaz de la aplicación
    tabs = st.tabs(["Player Search and Results", "Player Radar Generation", "Scatter Plots", "Player Comparison"])

    # Primera pestaña: Player Search and Results (mantenida del código original)
    with tabs[0]:
        st.header("Player Search and Results")

        available_seasons = sorted(combined_data['Season'].unique())
        selected_seasons = st.multiselect("Selecciona las temporadas:", available_seasons)

        filtered_data = combined_data[combined_data['Season'].isin(selected_seasons)]

        jugadores_disponibles = sorted(filtered_data['Full name'].unique())
        jugadores_seleccionados = st.multiselect("Selecciona los jugadores:", jugadores_disponibles)

        posicion_seleccionada = st.selectbox("Selecciona la posición del jugador:", metricas_por_posicion.keys())
        metricas_filtradas = metricas_por_posicion[posicion_seleccionada]

        todas_las_metricas = sorted([col for col in combined_data.columns if col not in ['Full name', 'Season', 'Team logo']])
        metricas_adicionales = st.multiselect("Selecciona métricas adicionales:", todas_las_metricas)

        metricas_finales = [metrica for metrica in metricas_filtradas + metricas_adicionales if metrica in filtered_data.columns]

        if jugadores_seleccionados:
            jugadores_data = filtered_data[filtered_data['Full name'].isin(jugadores_seleccionados)][['Full name', 'Team logo'] + metricas_finales]
            st.markdown(jugadores_data.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Segunda pestaña: Player Radar Generation (mantenida y mejorada)
    with tabs[1]:
        st.header("Player Radar Generation")

        if 'Competition' not in combined_data.columns:
            st.error("La columna 'Competition' no se encontró en los datos combinados.")
        else:
            selected_league = st.selectbox("Selecciona la liga:", sorted(combined_data['Competition'].unique()))
            filtered_teams = combined_data[combined_data['Competition'] == selected_league]['Team'].unique()
            selected_team = st.selectbox("Selecciona el equipo:", sorted(filtered_teams))

            age_range = st.slider("Selecciona el rango de edad:", int(combined_data['Age'].min()), int(combined_data['Age'].max()), (18, 35))
            selected_foot = st.selectbox("Selecciona el pie preferido:", sorted(combined_data['Foot'].unique()))

            jugadores_filtrados = combined_data[
                (combined_data['Competition'] == selected_league) &
                (combined_data['Team'] == selected_team) &
                (combined_data['Age'].between(age_range[0], age_range[1])) &
                (combined_data['Foot'] == selected_foot)
            ]['Full name'].unique()

            selected_player = st.selectbox("Selecciona el jugador:", sorted(jugadores_filtrados))

            if selected_player:
                st.write(f"Mostrando radar para el jugador: {selected_player}")
                jugador_data = combined_data[combined_data['Full name'] == selected_player]
                posicion_seleccionada = st.selectbox("Selecciona la posición del jugador para el radar:", metricas_por_posicion.keys())
                metricas_para_radar = metricas_por_posicion[posicion_seleccionada]

                valores_jugador = [jugador_data[metrica].values[0] if metrica in jugador_data.columns else 0 for metrica in metricas_para_radar]

                if valores_jugador:
                    fig = generate_radar_chart(jugador_data, metricas_para_radar, selected_player)
                    st.pyplot(fig)

                    compare_with_league = st.checkbox("Comparar con la media de la liga")
                    if compare_with_league:
                        league_avg = combined_data[combined_data['Competition'] == selected_league][metricas_para_radar].mean()
                        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
                        
                        ax.plot(angles, valores_jugador, 'o-', linewidth=2, label=selected_player)
                        ax.fill(angles, valores_jugador, alpha=0.25)
                        
                        league_values = league_avg.values.tolist() + league_avg.values.tolist()[:1]
                        ax.plot(angles, league_values, 'o-', linewidth=2, label='Liga Promedio')
                        ax.fill(angles, league_values, alpha=0.25)
                        
                        ax.set_xticks(angles[:-1])
                        ax.set_xticklabels(metricas_para_radar)
                        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
                        
                        st.pyplot(fig)

    # Tercera pestaña: Scatter Plots (nueva funcionalidad)
    with tabs[2]:
        st.header("Scatter Plots")
        
        all_metrics = [col for col in combined_data.columns if col not in ['Full name', 'Team', 'Competition', 'Season']]
        x_metric = st.selectbox("Selecciona la métrica para el eje X:", all_metrics)
        y_metric = st.selectbox("Selecciona la métrica para el eje Y:", [m for m in all_metrics if m != x_metric])
        
        highlight_player = st.selectbox("Resaltar jugador (opcional):", [''] + list(combined_data['Full name'].unique()))
        
        if highlight_player == '':
            highlight_player = None
        
        scatter_fig = generate_scatter_plot(combined_data, x_metric, y_metric, highlight_player)
        st.pyplot(scatter_fig)

    # Cuarta pestaña: Player Comparison (nueva funcionalidad)
    with tabs[3]:
        st.header("Player Comparison")
        
        players_to_compare = st.multiselect("Selecciona jugadores para comparar:", combined_data['Full name'].unique(), max_selections=3)
        
        if len(players_to_compare) > 1:
            comparison_data = combined_data[combined_data['Full name'].isin(players_to_compare)]
            
            metrics_to_compare = st.multiselect("Selecciona métricas para comparar:", all_metrics, default=all_metrics[:5])
            
            if metrics_to_compare:
                fig, ax = plt.subplots(figsize=(12, 6))
                comparison_data.set_index('Full name')[metrics_to_compare].plot(kind='bar', ax=ax)
                plt.title("Comparación de Jugadores")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                st.write("Tabla de Comparación:")
                st.dataframe(comparison_data[['Full name'] + metrics_to_compare])
        else:
            st.write("Selecciona al menos dos jugadores para comparar.")

# Agregar un footer con información sobre la aplicación
st.markdown("---")
st.markdown("Desarrollado por [Tu Nombre/Equipo]. Datos proporcionados por [Fuente de Datos].")
