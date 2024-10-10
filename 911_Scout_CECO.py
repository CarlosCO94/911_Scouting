import streamlit as st
import pandas as pd
import requests
import re  # Para usar expresiones regulares
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

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

        # Verificar si la columna 'Season' existe antes de continuar
        if 'Season' in combined_data.columns:
            st.sidebar.header("Opciones de Comparación de Jugadores")

            # Multiselect para seleccionar temporadas
            available_seasons = sorted(combined_data['Season'].unique())
            selected_seasons = st.sidebar.multiselect("Selecciona las temporadas:", available_seasons)

            # Filtrar los datos para las temporadas seleccionadas
            filtered_data = combined_data[combined_data['Season'].isin(selected_seasons)]

            # Multiselect para seleccionar jugadores
            jugadores_disponibles = sorted(filtered_data['Full name'].unique())
            jugadores_seleccionados = st.sidebar.multiselect("Selecciona los jugadores:", jugadores_disponibles)

            # Select box para seleccionar la posición del jugador y mostrar las métricas correspondientes
            posicion_seleccionada = st.sidebar.selectbox("Selecciona la posición del jugador:", metricas_por_posicion.keys())
            metricas_filtradas = metricas_por_posicion[posicion_seleccionada]

            # Multiselect para seleccionar métricas adicionales
            todas_las_metricas = sorted([col for col in combined_data.columns if col not in ['Full name', 'Season', 'Team logo']])
            metricas_adicionales = st.sidebar.multiselect("Selecciona métricas adicionales:", todas_las_metricas)

            # Unir las métricas por posición y las métricas adicionales seleccionadas
            metricas_finales = list(set(metricas_filtradas + metricas_adicionales))

            # Mostrar los datos de los jugadores seleccionados con las métricas correspondientes y el logo del equipo
            if jugadores_seleccionados:
                jugadores_data = filtered_data[filtered_data['Full name'].isin(jugadores_seleccionados)][['Full name', 'Team logo'] + metricas_finales]

                # Construir la tabla HTML
                html_table = '<table border="1"><tr><th>Jugador</th><th>Logo</th>'
                html_table += ''.join([f'<th>{metrica}</th>' for metrica in metricas_finales])
                html_table += '</tr>'

                for _, row in jugadores_data.iterrows():
                    html_table += f'<tr><td>{row["Full name"]}</td><td><img src="{row["Team logo"]}" width="50"></td>'
                    for metrica in metricas_finales:
                        value = row[metrica]
                        cell_color = 'background-color: yellow;' if value == jugadores_data[metrica].max() else ''
                        html_table += f'<td style="{cell_color}">{value}</td>'
                    html_table += '</tr>'

                html_table += '</table>'

                # Mostrar la tabla HTML en Streamlit
                st.markdown(html_table, unsafe_allow_html=True)
        else:
            st.error("La columna 'Season' no está presente en los datos combinados.")
    else:
        st.error("No se encontraron datos en los archivos CSV proporcionados.")
