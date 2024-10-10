import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Añadir CSS personalizado para el diseño de las pestañas
st.markdown("""
    <style>
        .stTabs [role="tablist"] {
            border-bottom: 2px solid #E694FF;
        }
        .stTabs [role="tab"] {
            background: #333;
            color: white;
            font-weight: bold;
            border: 1px solid #E694FF;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
            padding: 10px;
            cursor: pointer;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background: #E694FF;
            color: black;
        }
        .stTabs [role="tabpanel"] {
            border: 1px solid #E694FF;
            padding: 20px;
            background: #f5f5f5;
        }
    </style>
""", unsafe_allow_html=True)

# Diccionario de métricas por posición
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

# URL base para acceder a los archivos directamente en GitHub
base_raw_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"

# URL de la API de GitHub para obtener el contenido de la carpeta "Main APP"
api_url = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Función para cargar datos CSV con caché
@st.cache_data
def cargar_datos_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo: {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# Obtener la lista de archivos CSV en la carpeta "Main APP" del repositorio utilizando la API de GitHub
file_urls = []
try:
    response = requests.get(api_url)
    if response.status_code == 200:
        archivos = response.json()
        # Generar la URL de descarga directa para cada archivo CSV encontrado
        file_urls = [base_raw_url + file['name'] for file in archivos if file['name'].endswith('.csv')]
        file_names = [file['name'] for file in archivos if file['name'].endswith('.csv')]
    else:
        st.error(f"Error al acceder a la carpeta Main APP: {response.status_code}")
except requests.RequestException as e:
    st.error(f"Error de red al intentar acceder a la carpeta Main APP: {e}")

# Verificar que se encontraron archivos CSV
if not file_urls:
    st.error("No se encontraron archivos CSV en la carpeta Main APP.")
else:
    data_frames = []
    for url, name in zip(file_urls, file_names):
        df = cargar_datos_csv(url)
        if not df.empty:
            # Extraer la temporada del nombre del archivo usando expresiones regulares
            match = re.search(r'(\d{4}(?:-\d{2,4})?)', name)
            if match:
                season = match.group(1)
                df['Season'] = season  # Añadir la columna 'Season' al DataFrame
            else:
                df['Season'] = 'Desconocida'  # Asignar 'Desconocida' si no se encuentra la temporada
            data_frames.append(df)

    # Combinar los dataframes si hay más de uno
    if data_frames:
        combined_data = pd.concat(data_frames, ignore_index=True)

        # Verificar si las columnas 'Full name' y 'Team logo' existen antes de continuar
        required_columns = ['Full name', 'Team logo']
        missing_columns = [col for col in required_columns if col not in combined_data.columns]
        if missing_columns:
            st.error(f"Las siguientes columnas necesarias no están presentes en los datos: {', '.join(missing_columns)}")
        else:
            # Crear pestañas para organizar la interfaz de la aplicación
            tabs = st.tabs(["Player Search and Results", "Player Radar Generation", "Scatter Plots"])

            # Primera pestaña: Player Search and Results
            with tabs[0]:
                st.header("Player Search and Results")

                # Multiselect para seleccionar temporadas
                available_seasons = sorted(combined_data['Season'].unique())
                selected_seasons = st.multiselect("Selecciona las temporadas:", available_seasons)

                # Filtrar los datos para las temporadas seleccionadas
                filtered_data = combined_data[combined_data['Season'].isin(selected_seasons)]

                # Multiselect para seleccionar jugadores
                jugadores_disponibles = sorted(filtered_data['Full name'].unique())
                jugadores_seleccionados = st.multiselect("Selecciona los jugadores:", jugadores_disponibles)

                # Select box para seleccionar la posición del jugador y mostrar las métricas correspondientes
                posicion_seleccionada = st.selectbox("Selecciona la posición del jugador:", metricas_por_posicion.keys())
                metricas_filtradas = metricas_por_posicion[posicion_seleccionada]

                # Multiselect para seleccionar métricas adicionales
                todas_las_metricas = sorted([col for col in combined_data.columns if col not in ['Full name', 'Season', 'Team logo']])
                metricas_adicionales = st.multiselect("Selecciona métricas adicionales:", todas_las_metricas)

                # Unir las métricas por posición y las métricas adicionales seleccionadas
                metricas_finales = [metrica for metrica in metricas_filtradas + metricas_adicionales if metrica in filtered_data.columns]

                # Mostrar los datos de los jugadores seleccionados con las métricas correspondientes y el logo del equipo
                if jugadores_seleccionados:
                    jugadores_data = filtered_data[filtered_data['Full name'].isin(jugadores_seleccionados)][['Full name', 'Team logo'] + metricas_finales]

                    # Construir la tabla HTML con los logos en la primera fila y nombres de jugadores centrados
                    html_table = '<table border="1" style="text-align: center;"><tr><th>Logo</th>'
                    html_table += ''.join([f'<th><img src="{jugadores_data.loc[jugadores_data["Full name"] == jugador, "Team logo"].values[0]}" width="50"></th>' for jugador in jugadores_seleccionados])
                    html_table += '</tr><tr><th>Jugador</th>'
                    html_table += ''.join([f'<th style="text-align: center;">{jugador}</th>' for jugador in jugadores_seleccionados])
                    html_table += '</tr>'

                    for metrica in metricas_finales:
                        html_table += f'<tr><td>{metrica}</td>'
                        for jugador in jugadores_seleccionados:
                            value = jugadores_data.loc[jugadores_data['Full name'] == jugador, metrica].values[0] if metrica in jugadores_data else ''
                            cell_color = 'background-color: yellow;' if value == jugadores_data[metrica].max() else ''
                            html_table += f'<td style="{cell_color}; text-align: center;">{value}</td>'
                        html_table += '</tr>'

                    html_table += '</table>'

                    # Mostrar la tabla HTML en la pestaña "Player Search and Results"
                    st.markdown(html_table, unsafe_allow_html=True)

            # Segunda pestaña: Player Radar Generation
            with tabs[1]:
                st.header("Player Radar Generation")
                st.write("Aquí se generará el radar de jugadores.")

            # Tercera pestaña: Scatter Plots
            with tabs[2]:
                st.header("Scatter Plots")
                st.write("Aquí se mostrarán los gráficos de dispersión.")
