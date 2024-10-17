import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote
from scipy.spatial import distance

# URL base de la carpeta en GitHub
base_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"

# Función para obtener los archivos CSV
def get_csv_files():
    response = requests.get("https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP")
    files = response.json()
    csv_files = [file['name'] for file in files if file['name'].endswith('.csv')]
    return csv_files

# Cargar archivos CSV
def load_csv(file_name):
    encoded_file_name = quote(file_name)
    url = base_url + encoded_file_name
    data = pd.read_csv(url, encoding='utf-8')
    return data

# Obtener archivos CSV
csv_files = get_csv_files()

# Extraer temporadas únicas y ligas
temporadas = set()
ligas = set()
for file in csv_files:
    temp = file.split(" ")[-1].replace(".csv", "")
    temporadas.add(temp)
    liga = " ".join(file.split(" ")[:-1])  # Asumiendo que el nombre de la liga está antes de la temporada
    ligas.add(liga)

# Configuración de la barra lateral
st.sidebar.title('Filtros')

# Seleccionar temporadas
selected_temporadas = st.sidebar.multiselect("Selecciona las temporadas:", sorted(temporadas))

# Seleccionar ligas
selected_ligas = st.sidebar.multiselect("Selecciona las ligas:", sorted(ligas))

# Seleccionar jugador por nombre completo
player_name = None
if selected_temporadas and selected_ligas:
    # Cargar los datos de todos los jugadores de las temporadas y ligas seleccionadas
    players_data = []
    for file_name in csv_files:
        if any(temp in file_name for temp in selected_temporadas) and any(liga in file_name for liga in selected_ligas):
            players_df = load_csv(file_name)
            if not players_df.empty:
                players_data.append(players_df)

    # Concatenar todos los DataFrames cargados
    if players_data:
        players_df = pd.concat(players_data, ignore_index=True)

        # Verificar que el DataFrame se haya cargado correctamente
        if 'Full name' in players_df.columns:
            player_name = st.sidebar.selectbox('Selecciona un jugador', players_df['Full name'].unique())

            # Mostrar el jugador seleccionado
            if player_name:
                selected_player = players_df[players_df['Full name'] == player_name]
                st.write(f"**Jugador Seleccionado:** {selected_player['Full name'].values[0]}")
                st.write(f"**Equipo:** {selected_player['Team'].values[0]}")
                st.write(f"**Posición:** {selected_player['Position'].values[0]}")
                st.write(f"**Edad:** {selected_player['Age'].values[0]}")

                # Seleccionar posición
                selected_position = st.sidebar.selectbox("Selecciona la posición:", ['Todos', 
                    'Arquero', 'Defensa', 'Lateral Izquierdo', 'Lateral Derecho', 
                    'Mediocampista Defensivo', 'Mediocampista Central', 
                    'Mediocampista Ofensivo', 'Extremos', 'Delantero'])

                # Filtrar por rango de edad
                age_range = st.sidebar.slider("Selecciona el rango de edad:", 16, 40, (20, 30))

                # Botón de submit
                if st.sidebar.button('Submit'):
                    # Filtrar por posición según la selección
                    filtered_players = players_df
                    if selected_position != 'Todos':
                        if selected_position == 'Arquero':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('GK', na=False)]
                        elif selected_position == 'Defensa':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('CB', na=False)]
                        elif selected_position == 'Lateral Izquierdo':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('LB|LWB', na=False)]
                        elif selected_position == 'Lateral Derecho':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('RB|RWB', na=False)]
                        elif selected_position == 'Mediocampista Defensivo':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('DMF', na=False)]
                        elif selected_position == 'Mediocampista Central':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('CMF', na=False)]
                        elif selected_position == 'Mediocampista Ofensivo':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('AMF', na=False)]
                        elif selected_position == 'Extremos':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('RW|LW|LWF|RWF', na=False)]
                        elif selected_position == 'Delantero':
                            filtered_players = filtered_players[filtered_players['Position'].str.contains('CF', na=False)]

                    # Aplicar filtro de rango de edad
                    filtered_players = filtered_players[(filtered_players['Age'] >= age_range[0]) & (filtered_players['Age'] <= age_range[1])]

                    # Calcular similitud euclidiana
                    metrics_columns = ['Goals', 'Assists', 'xG', 'xA', 'Shots', 'xG against', 'Interceptions per 90']  # Columnas de métricas relevantes
                    player_metrics = selected_player[metrics_columns].values.flatten()  # Métricas del jugador seleccionado
                    similar_players = []

                    for index, player in filtered_players.iterrows():
                        other_player_metrics = player[metrics_columns].values
                        euclidean_distance = distance.euclidean(player_metrics, other_player_metrics)
                        similar_players.append((player['Full name'], euclidean_distance))

                    # Ordenar jugadores por distancia euclidiana (menor distancia = más similares)
                    similar_players.sort(key=lambda x: x[1])

                    # Mostrar jugadores similares
                    st.write("**Jugadores Similares:**")
                    for name, dist in similar_players[:5]:  # Mostrar los 5 jugadores más similares
                        st.write(f"- {name} (Distancia: {dist:.2f})")
    else:
        st.error("No se encontraron datos de jugadores.")
else:
    st.error("Selecciona al menos una temporada y una liga.")
