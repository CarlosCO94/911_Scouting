import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Configuración para que la página siempre se ejecute en modo wide
st.set_page_config(layout="wide")

# Función para cargar datos CSV desde una URL
@st.cache_data
def cargar_csv_desde_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error(f"Error al cargar el archivo desde {url}. Código de estado: {response.status_code}")
        return pd.DataFrame()

# URLs de los archivos necesarios
url_metricas_traducidas = "https://github.com/CarlosCO94/911_Scouting/blob/main/Traducci%C3%B3n_Metricas.csv?raw=true"
url_logos_equipos = "https://github.com/CarlosCO94/911_Scouting/blob/main/Wyscout_Logo_URL.csv?raw=true"
url_datos_jugadores_base = "https://api.github.com/repos/CarlosCO94/911_Scouting/contents/Main%20APP"

# Cargar las métricas traducidas y los logos de equipos
metricas_traducidas_df = cargar_csv_desde_url(url_metricas_traducidas)
logos_equipos_df = cargar_csv_desde_url(url_logos_equipos)

# Mostrar las columnas del DataFrame para verificar los nombres correctos
st.write("Columnas del archivo de métricas traducidas:", metricas_traducidas_df.columns.tolist())

# Convertir las métricas traducidas a un diccionario para una traducción rápida
# Verificar que los nombres de las columnas coincidan con lo esperado
if 'Métrica Original' in metricas_traducidas_df.columns and 'Métrica Traducida' in metricas_traducidas_df.columns:
    diccionario_traducciones = dict(zip(metricas_traducidas_df['Métrica Original'], metricas_traducidas_df['Métrica Traducida']))
else:
    st.error("El archivo de métricas traducidas no contiene las columnas 'Métrica Original' y 'Métrica Traducida'. Verifica el formato del archivo.")

