import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote

# Configuración de la página en modo wide
st.set_page_config(page_title="911 Scouting", layout="wide")

# URL base de la carpeta en GitHub
base_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Main%20APP/"

def get_csv_files():
    response = requests.get("https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP")
    
    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        files = response.json()
        # Asegurarse de que la respuesta sea una lista
        if isinstance(files, list):
            csv_files = [file['name'] for file in files if isinstance(file, dict) and file['name'].endswith('.csv')]
            return csv_files
        else:
            st.error("Error: La respuesta de la API no es una lista.")
            return []
    else:
        st.error("Error al obtener los archivos CSV. Código de estado: {}".format(response.status_code))
        return []

# Cargar archivos CSV
def load_csv(file_name):
    encoded_file_name = quote(file_name)
    url = base_url + encoded_file_name
    data = pd.read_csv(url, encoding='utf-8')
    return data

# Título y subtítulo
st.title("911 Scouting")
st.subheader("By CECO")
st.title("Búsqueda General")

# Obtener archivos CSV
csv_files = get_csv_files()

# Extraer temporadas únicas
temporadas = set()
for file in csv_files:
    temporada = file.split(" ")[-1].replace(".csv", "")
    temporadas.add(temporada)

# Seleccionar temporada
selected_temporada = st.sidebar.selectbox("Selecciona una temporada:", sorted(temporadas))

# Filtrar archivos CSV por la temporada seleccionada
filtered_files = [file for file in csv_files if selected_temporada in file]

# Agregar "Todos" a las opciones
options = ['Todos'] + filtered_files

# Crear un select box para la Liga donde se pueden seleccionar varios archivos CSV
selected_files = st.multiselect(
    "Selecciona las ligas (archivos CSV):",
    options=options,
    default=['Todos']  # Selecciona "Todos" por defecto
)

# Cargar los archivos seleccionados
data_frames = []

# Verificar si se seleccionó "Todos"
if "Todos" in selected_files:
    selected_files = filtered_files  # Selecciona todos los archivos disponibles

for file in selected_files:
    data = load_csv(file)
    data_frames.append(data)

# Combinar los DataFrames si hay archivos seleccionados
if data_frames:
    combined_data = pd.concat(data_frames, ignore_index=True)

    # Agregar un filtro de rango de edad
    age_range = st.slider("Selecciona un rango de edad:", 15, 40, (20, 30))

    # Filtrar por rango de edad
    combined_data = combined_data[(combined_data['Age'] >= age_range[0]) & (combined_data['Age'] <= age_range[1])]

    # Agregar un filtro de rango de partidos jugados
    matches_played_range = st.slider("Selecciona un rango de partidos jugados:", 0, 100, (0, 100))

    # Filtrar por rango de partidos jugados
    combined_data = combined_data[(combined_data['Matches played'] >= matches_played_range[0]) & 
                                  (combined_data['Matches played'] <= matches_played_range[1])]

    # Agregar un filtro de rango de minutos jugados
    minutes_played_range = st.slider("Selecciona un rango de minutos jugados:", 0, 5000, (0, 5000))

    # Filtrar por rango de minutos jugados
    combined_data = combined_data[(combined_data['Minutes played'] >= minutes_played_range[0]) & 
                                  (combined_data['Minutes played'] <= minutes_played_range[1])]

    # Agregar un select box para Pierna
    foot_options = ['Todos'] + combined_data['Foot'].unique().tolist()  # Obtener opciones únicas de pie
    selected_foot = st.selectbox("Selecciona la pierna:", foot_options)

    # Filtrar por pierna si no se seleccionó "Todos"
    if selected_foot != 'Todos':
        combined_data = combined_data[combined_data['Foot'] == selected_foot]

    # Agregar un select box para Posición Principal en el orden correcto
    position_options = [
        'Todos', 
        'Arquero', 
        'Defensa', 
        'Lateral Izquierdo', 
        'Lateral Derecho', 
        'Mediocampista Defensivo', 
        'Mediocampista Central', 
        'Mediocampista Ofensivo', 
        'Extremos', 
        'Delantero'
    ]
    selected_position = st.selectbox("Selecciona la posición principal:", position_options)

    # Filtrar por posición principal según la selección
    if selected_position == 'Arquero':
        combined_data = combined_data[combined_data['Position'].str.contains('GK', na=False)]
    elif selected_position == 'Defensa':
        combined_data = combined_data[combined_data['Position'].str.contains('CB', na=False)]
    elif selected_position == 'Lateral Izquierdo':
        combined_data = combined_data[combined_data['Position'].str.contains('LB|LWB', na=False)]
    elif selected_position == 'Lateral Derecho':
        combined_data = combined_data[combined_data['Position'].str.contains('RB|RWB', na=False)]
    elif selected_position == 'Mediocampista Defensivo':
        combined_data = combined_data[combined_data['Position'].str.contains('DMF', na=False)]
    elif selected_position == 'Mediocampista Central':
        combined_data = combined_data[combined_data['Position'].str.contains('CMF', na=False)]
    elif selected_position == 'Mediocampista Ofensivo':
        combined_data = combined_data[combined_data['Position'].str.contains('AMF', na=False)]
    elif selected_position == 'Extremos':
        combined_data = combined_data[combined_data['Position'].str.contains('RW|LW|LWF|RWF', na=False)]
    elif selected_position == 'Delantero':
        combined_data = combined_data[combined_data['Position'].str.contains('CF', na=False)]

    # Agregar un select box para Equipo
    team_options = ['Todos'] + combined_data['Team'].unique().tolist()  # Obtener opciones únicas de equipo
    selected_team = st.selectbox("Selecciona el equipo:", team_options)

    # Filtrar por equipo si no se seleccionó "Todos"
    if selected_team != 'Todos':
        combined_data = combined_data[combined_data['Team'] == selected_team]

    # Mostrar datos combinados
    if "Todos" in selected_files:
        st.write("Datos combinados: Todos")
    else:
        st.write("Datos combinados:")
    
    # Mostrar solo las columnas seleccionadas, incluyendo Competencia y Team logo
    result_columns = ['Full name', 'Team logo', 'Team', 'Competition', 'Foot', 'Age', 'Height', 'Matches played', 'Minutes played']
    
    # Mostrar el logo del equipo utilizando HTML
    combined_data['Team logo'] = combined_data['Team logo'].apply(lambda x: f'<img src="{x}" width="50" height="50">')
    
    # Mostrar la tabla con los logos usando st.markdown
    # Centrar los datos y poner encabezados en negrita
    html_table = combined_data[result_columns].to_html(escape=False, index=False)
    html_table = html_table.replace('<th>', '<th style="text-align: center; font-weight: bold;">')  # Encabezados en negrita y centrados
    html_table = html_table.replace('<td>', '<td style="text-align: center;">')  # Datos centrados

    st.markdown(html_table, unsafe_allow_html=True)

# Aquí puedes agregar más lógica específica para la búsqueda general
