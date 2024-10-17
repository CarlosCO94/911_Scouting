import pandas as pd
import streamlit as st

# URL base de la carpeta en GitHub
base_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"
league_lookup_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Ligas_lookup.csv"

# Función para obtener archivos CSV
@st.cache_data
def load_csv(url):
    try:
        data = pd.read_csv(url, encoding='utf-8')
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo desde {url}: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío

# Cargar la información de las ligas
league_lookup = load_csv(league_lookup_url)

# Configuración de la barra lateral
st.sidebar.title('Filtros')

# Seleccionar la temporada
season = st.sidebar.selectbox('Selecciona la Temporada', league_lookup['Season'].unique(), index=list(league_lookup['Season'].unique()).index('2024'))

# Cargar los datos de todos los jugadores
players_df = pd.concat([load_csv(f"{base_url}{lg} {season}.csv".replace(" ", "%20")) for lg in league_lookup['League'].unique()])

# Verificar que el DataFrame se haya cargado correctamente
if not players_df.empty and 'Full name' in players_df.columns:
    # Seleccionar jugador por nombre completo (Full name) en la barra lateral
    player_name = st.sidebar.selectbox('Selecciona un jugador', players_df['Full name'].unique())

    # Mostrar el jugador seleccionado
    if player_name:
        selected_player = players_df[players_df['Full name'] == player_name]
        st.write(f"**Jugador Seleccionado:** {selected_player['Full name'].values[0]}")
        st.write(f"**Equipo:** {selected_player['Team'].values[0]}")
        st.write(f"**Posición:** {selected_player['Position'].values[0]}")
        st.write(f"**Edad:** {selected_player['Age'].values[0]}")
else:
    st.error("No se pudo cargar los datos de jugadores o no se encontró la columna 'Full name'.")
