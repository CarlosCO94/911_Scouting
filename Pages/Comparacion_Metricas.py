import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

# URL base de la carpeta en GitHub
base_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"

# Diccionario con las posiciones y métricas asociadas
metrics_by_position = {
    'Portero': ["Matches played", "Minutes played", "Conceded goals per 90", "xG against per 90", "Prevented goals per 90", "Save rate, %", 
                "Exits per 90", "Aerial duels per 90", "Back passes received as GK per 90", 
                "Accurate passes, %", "Accurate forward passes, %", "Accurate long passes, %"],
    'Defensa': ["Matches played", "Minutes played", "Accelerations per 90", "Progressive runs per 90", "Aerial duels per 90", "Aerial duels won, %", 
                "Defensive duels won, %", "Duels won, %", "Sliding tackles per 90", "Interceptions per 90", 
                "Key passes per 90", "Short / medium passes per 90", "Forward passes per 90", "Long passes per 90", 
                "Passes per 90", "PAdj Interceptions", "Accurate passes to final third, %", "Accurate forward passes, %", 
                "Accurate back passes, %", "Accurate long passes, %", "Accurate passes, %"],
    'Lateral': ["Matches played", "Minutes played", "Successful attacking actions per 90", "Successful defensive actions per 90", "Accelerations per 90", 
                "Progressive runs per 90", "Crosses to goalie box per 90", "Crosses from final third per 90", 
                "Aerial duels won, %", "Offensive duels won, %", "Defensive duels won, %", "Defensive duels per 90", 
                "Duels won, %", "Interceptions per 90", "Passes per 90", "Forward passes per 90", 
                "Accurate passes to penalty area, %", "Received passes per 90", "Accurate passes to final third, %", 
                "Accurate through passes, %", "Accurate forward passes, %", "Accurate progressive passes, %", 
                "Third assists per 90", "xA per 90"],
    'Mediocampista': ["Matches played", "Minutes played", "Assists per 90", "xA per 90", "Offensive duels won, %", "Aerial duels won, %", 
                      "Defensive duels won, %", "Interceptions per 90", "Received passes per 90", 
                      "Accurate short / medium passes, %", "Accurate passes to final third, %", 
                      "Accurate long passes, %", "Accurate progressive passes, %", "Successful dribbles, %", 
                      "xG per 90", "Goals per 90"],
    'Extremos': ["Matches played", "Minutes played", "xG per 90", "Goals per 90", "Assists per 90", "xA per 90", "Received passes per 90", 
                 "Accurate crosses, %", "Accurate through passes, %", "Accurate progressive passes, %", 
                 "Crosses to goalie box per 90", "Accurate passes to penalty area, %", "Offensive duels won, %", 
                 "Defensive duels won, %", "Interceptions per 90", "Successful dribbles, %"],
    'Delantero': ["Matches played", "Minutes played", "Goals per 90", "Head goals per 90", "Non-penalty goals per 90", "Goal conversion, %", 
                  "xG per 90", "xA per 90", "Assists per 90", "Key passes per 90", "Passes per 90", 
                  "Passes to penalty area per 90", "Passes to final third per 90", "Accurate passes, %", 
                  "Accurate passes to final third, %", "Aerial duels won, %", "Duels won, %", 
                  "Shots per 90", "Shots on target, %", "Touches in box per 90"]
}

# Función para obtener los archivos CSV
@st.cache_data  # Almacenar en caché para mejorar el rendimiento
def get_csv_files():
    try:
        response = requests.get("https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP")
        files = response.json()
        csv_files = [file['name'] for file in files if file['name'].endswith('.csv')]
        return csv_files
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener archivos CSV: {e}")
        return []

# Cargar archivos CSV
@st.cache_data  # Almacenar en caché para mejorar el rendimiento
def load_csv(file_name):
    try:
        encoded_file_name = quote(file_name)  # Asegura que los nombres de archivo con espacios o caracteres especiales se codifiquen correctamente
        url = base_url + encoded_file_name
        data = pd.read_csv(url, encoding='utf-8')
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo {file_name}: {e}")
        return pd.DataFrame()

# Obtener lista de archivos CSV desde el repositorio
csv_files = get_csv_files()

# Verificar si hay archivos CSV disponibles
if csv_files:
    # Cargar y combinar todos los archivos CSV
    combined_data = pd.DataFrame()  # DataFrame vacío para combinar todos los CSV

    for csv_file in csv_files:
        df = load_csv(csv_file)
        combined_data = pd.concat([combined_data, df], ignore_index=True)

    # Verificar si la columna 'Wyscout id' existe en el conjunto de datos
    if 'Wyscout id' in combined_data.columns:
        # Agrupar por 'Wyscout id' y sumar métricas numéricas
        combined_data_grouped = combined_data.groupby('Wyscout id', as_index=False).agg({
            'Matches played': 'sum',
            'Minutes played': 'sum',
            'Goals': 'sum',
            'xG': 'sum',
            'Assists': 'sum',
            'xA': 'sum',
            'Duels per 90': 'mean',
            'Duels won, %': 'mean',
            'Successful defensive actions per 90': 'mean',
            'Defensive duels per 90': 'mean',
            'Defensive duels won, %': 'mean',
            'Aerial duels per 90': 'mean',
            'Aerial duels won, %': 'mean',
            'Sliding tackles per 90': 'mean',
            'PAdj Sliding tackles': 'mean',
            'Shots blocked per 90': 'mean',
            'Interceptions per 90': 'mean',
            'PAdj Interceptions': 'mean',
            'Fouls per 90': 'mean',
            'Yellow cards': 'sum',
            'Yellow cards per 90': 'mean',
            'Red cards': 'sum',
            'Red cards per 90': 'mean',
            'Successful attacking actions per 90': 'mean',
            'Non-penalty goals': 'sum',
            'Non-penalty goals per 90': 'mean',
            'xG per 90': 'mean',
            'Head goals': 'sum',
            'Head goals per 90': 'mean',
            'Shots': 'sum',
            'Shots per 90': 'mean',
            'Shots on target, %': 'mean',
            'Goal conversion, %': 'mean',
            'Assists per 90': 'mean',
            'Crosses per 90': 'mean',
            'Accurate crosses, %': 'mean',
            'Crosses from left flank per 90': 'mean',
            'Accurate crosses from left flank, %': 'mean',
            'Crosses from right flank per 90': 'mean',
            'Accurate crosses from right flank, %': 'mean',
            'Crosses to goalie box per 90': 'mean',
            'Dribbles per 90': 'mean',
            'Successful dribbles, %': 'mean',
            'Offensive duels per 90': 'mean',
            'Offensive duels won, %': 'mean',
            'Touches in box per 90': 'mean',
            'Progressive runs per 90': 'mean',
            'Accelerations per 90': 'mean',
            'Received passes per 90': 'mean',
            'Received long passes per 90': 'mean',
            'Fouls suffered per 90': 'mean',
            'Passes per 90': 'mean',
            'Accurate passes, %': 'mean',
            'Forward passes per 90': 'mean',
            'Accurate forward passes, %': 'mean',
            'Back passes per 90': 'mean',
            'Accurate back passes, %': 'mean',
                        'Short / medium passes per 90': 'mean',
            'Accurate short / medium passes, %': 'mean',
            'Long passes per 90': 'mean',
            'Accurate long passes, %': 'mean',
            'Average pass length, m': 'mean',
            'Average long pass length, m': 'mean',
            'xA per 90': 'mean',
            'Shot assists per 90': 'mean',
            'Second assists per 90': 'mean',
            'Third assists per 90': 'mean',
            'Smart passes per 90': 'mean',
            'Accurate smart passes, %': 'mean',
            'Key passes per 90': 'mean',
            'Passes to final third per 90': 'mean',
            'Accurate passes to final third, %': 'mean',
            'Passes to penalty area per 90': 'mean',
            'Accurate passes to penalty area, %': 'mean',
            'Through passes per 90': 'mean',
            'Accurate through passes, %': 'mean',
            'Deep completions per 90': 'mean',
            'Deep completed crosses per 90': 'mean',
            'Progressive passes per 90': 'mean',
            'Accurate progressive passes, %': 'mean',
            'Accurate vertical passes, %': 'mean',
            'Vertical passes per 90': 'mean',
            'Conceded goals': 'sum',
            'Conceded goals per 90': 'mean',
            'Shots against': 'sum',
            'Shots against per 90': 'mean',
            'Clean sheets': 'sum',
            'Save rate, %': 'mean',
            'xG against': 'sum',
            'xG against per 90': 'mean',
            'Prevented goals': 'sum',
            'Prevented goals per 90': 'mean',
            'Back passes received as GK per 90': 'mean',
            'Exits per 90': 'mean',
            'Free kicks per 90': 'mean',
            'Direct free kicks per 90': 'mean',
            'Direct free kicks on target, %': 'mean',
            'Corners per 90': 'mean',
            'Penalties taken': 'sum',
            'Penalty conversion, %': 'mean',
            'Full name': 'first',  # Agregar el nombre del jugador
            'Team logo': 'first'    # Agregar el logo del equipo
        })

        # Crear un multiselect para elegir varios jugadores
        unique_players = combined_data_grouped['Full name'].unique()
        selected_players = st.multiselect('Selecciona dos o más jugadores', unique_players)

        # Seleccionar la posición del jugador
        position = st.selectbox("Selecciona la posición del jugador", list(metrics_by_position.keys()))

        # Mostrar las métricas asociadas a la posición seleccionada automáticamente en la tabla
        if selected_players and position:
            selected_metrics = metrics_by_position[position]

            # Permitir que el usuario seleccione métricas adicionales
            additional_metrics = st.multiselect(
                "Selecciona métricas adicionales para agregar a la tabla",
                [metric for metric in combined_data_grouped.columns if metric not in selected_metrics]
            )

            # Combinar las métricas de la posición seleccionada con las métricas adicionales seleccionadas
            metrics_to_display = ['Full name', 'Team logo'] + selected_metrics + additional_metrics

            # Filtrar solo las métricas que existen en el DataFrame
            metrics_to_display = [metric for metric in metrics_to_display if metric in combined_data_grouped.columns]

            # Filtrar los datos según los jugadores seleccionados y las métricas correspondientes
            players_data = combined_data_grouped[combined_data_grouped['Full name'].isin(selected_players)][metrics_to_display]

            # Transponer la tabla
            transposed_data = players_data.set_index('Full name').T

            # Convertir la tabla en HTML con formato condicional y agregar escudos debajo del nombre del jugador
            def style_row(value, max_val):
                if isinstance(value, (int, float)):
                    if value == max_val:
                        return 'background-color: yellow; color: black; font-weight: bold;'
                return ''

            # Crear tabla HTML
            html_table = "<table border='1' style='border-collapse:collapse; width:100%; text-align:center;'><thead><tr><th>Métrica</th>"
            for player in transposed_data.columns:
                player_name = player
                team_logo = transposed_data.loc['Team logo', player]
                html_table += f"<th>{player_name}<br><img src='{team_logo}' width='50' style='display:block;margin:auto;'></th>"
            html_table += "</tr></thead><tbody>"

            for row in transposed_data.index:
                if row != 'Team logo':  # No volvemos a mostrar la fila de 'Team logo'
                    html_table += f"<tr><td>{row}</td>"
                    max_val = transposed_data.loc[row].max()
                    for value in transposed_data.loc[row]:
                        style = style_row(value, max_val)
                        html_table += f"<td style='{style}'>{value}</td>"
                    html_table += "</tr>"

            html_table += "</tbody></table>"

            # Mostrar la tabla en formato HTML
            st.markdown(html_table, unsafe_allow_html=True)

        else:
            st.write("Por favor selecciona al menos dos jugadores y una posición.")
    else:
        st.error("No se encontró la columna 'Wyscout id' en los archivos CSV.")
else:
    st.error("No se encontraron archivos CSV.")
