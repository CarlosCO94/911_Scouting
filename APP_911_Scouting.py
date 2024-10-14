import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote

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

# Título y subtítulo
st.title("911 Scouting")
st.subheader("By CECO")

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

# Cargar automáticamente todos los archivos filtrados
data_frames = []
for file in filtered_files:
    data = load_csv(file)
    data_frames.append(data)

# Aquí puedes agregar lógica para procesar los datos cargados si es necesario,
# pero no mostrar los datos combinados.

# Barra lateral para la navegación
st.sidebar.title("Navegación")
page = st.sidebar.radio("Selecciona una página:", ["Búsqueda General", "Comparación de Métricas", "% de Similitud", "Scoring", "Smart 11"])

# Cargar la página seleccionada
if page == "Búsqueda General":
    st.write("Contenido de Búsqueda General")
    # Aquí puedes agregar el contenido específico de la página
elif page == "Comparación de Métricas":
    st.write("Contenido de Comparación de Métricas")
    # Aquí puedes agregar el contenido específico de la página
elif page == "% de Similitud":
    st.write("Contenido de % de Similitud")
    # Aquí puedes agregar el contenido específico de la página
elif page == "Scoring":
    st.write("Contenido de Scoring")
    # Aquí puedes agregar el contenido específico de la página
elif page == "Smart 11":
    st.write("Contenido de Smart 11")
    # Aquí puedes agregar el contenido específico de la página
