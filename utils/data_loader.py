import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
import os
import pyarrow.parquet as pq
from urllib.parse import urljoin

def obtener_estructura_repositorio():
    """
    Define manualmente la estructura del repositorio de GitHub.
    Esta función evita problemas de acceso a la API de GitHub y web scraping.
    """
    # Estructura predefinida basada en el repositorio
    # https://github.com/CarlosCO94/911_Scouting/tree/main/Ligas_Parquet
    return {
        "temporadas": [
            {"nombre": "2021-2022", "carpeta": "2021-2022"},
            {"nombre": "2022-2023", "carpeta": "2022-2023"},
            {"nombre": "2023-2024", "carpeta": "2023-2024"}
        ],
        "ligas": {
            "2021-2022": [
                {"nombre": "Premier League", "archivo": "Premier_League.parquet"},
                {"nombre": "La Liga", "archivo": "La_Liga.parquet"},
                {"nombre": "Serie A", "archivo": "Serie_A.parquet"},
                {"nombre": "Bundesliga", "archivo": "Bundesliga.parquet"},
                {"nombre": "Ligue 1", "archivo": "Ligue_1.parquet"}
            ],
            "2022-2023": [
                {"nombre": "Premier League", "archivo": "Premier_League.parquet"},
                {"nombre": "La Liga", "archivo": "La_Liga.parquet"},
                {"nombre": "Serie A", "archivo": "Serie_A.parquet"},
                {"nombre": "Bundesliga", "archivo": "Bundesliga.parquet"},
                {"nombre": "Ligue 1", "archivo": "Ligue_1.parquet"}
            ],
            "2023-2024": [
                {"nombre": "Premier League", "archivo": "Premier_League.parquet"},
                {"nombre": "La Liga", "archivo": "La_Liga.parquet"},
                {"nombre": "Serie A", "archivo": "Serie_A.parquet"},
                {"nombre": "Bundesliga", "archivo": "Bundesliga.parquet"},
                {"nombre": "Ligue 1", "archivo": "Ligue_1.parquet"}
            ]
        }
    }

def construir_url_raw(temporada, archivo):
    """
    Construye la URL para el archivo raw en GitHub.
    """
    base_url = "https://raw.githubusercontent.com/CarlosCO94/911_Scouting/main/Ligas_Parquet"
    return f"{base_url}/{temporada}/{archivo}"

def descargar_parquet(url):
    """Descarga un archivo Parquet desde GitHub y lo carga como DataFrame."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanzar excepción si hay error HTTP
        
        # Guardar temporalmente el archivo
        with open('temp.parquet', 'wb') as f:
            f.write(response.content)
        
        # Leer el archivo Parquet
        data = pd.read_parquet('temp.parquet')
        
        # Eliminar archivo temporal
        if os.path.exists('temp.parquet'):
            os.remove('temp.parquet')
        
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error al descargar el archivo: {e}")
        return None
    except Exception as e:
        st.error(f"Error al procesar el archivo Parquet: {e}")
        # Intentar eliminar el archivo temporal si existe
        if os.path.exists('temp.parquet'):
            os.remove('temp.parquet')
        return None

def cargar_datos_github():
    """Carga datos desde el repositorio de GitHub."""
    try:
        # Obtener estructura del repositorio
        estructura = obtener_estructura_repositorio()
        
        # Mostrar selección de temporada
        temporadas = [temp["nombre"] for temp in estructura["temporadas"]]
        temporada_seleccionada = st.selectbox(
            "Selecciona una temporada:",
            temporadas
        )
        
        # Obtener ligas disponibles para la temporada seleccionada
        ligas_disponibles = estructura["ligas"].get(temporada_seleccionada, [])
        
        if ligas_disponibles:
            # Mostrar selección de liga
            opciones_ligas = {liga["nombre"]: liga["archivo"] for liga in ligas_disponibles}
            liga_seleccionada = st.selectbox(
                "Selecciona una liga:",
                list(opciones_ligas.keys())
            )
            
            # Botón para cargar el archivo seleccionado
            if st.button("Cargar datos"):
                archivo = opciones_ligas[liga_seleccionada]
                url_archivo = construir_url_raw(temporada_seleccionada, archivo)
                
                with st.spinner(f"Descargando y procesando datos de {liga_seleccionada} ({temporada_seleccionada})..."):
                    data = descargar_parquet(url_archivo)
                    
                    if data is not None:
                        # Guardar en la sesión
                        st.session_state['data'] = data
                        st.session_state['liga_actual'] = liga_seleccionada
                        st.session_state['temporada_actual'] = temporada_seleccionada
                        
                        # Mostrar información del dataset
                        st.success(f"¡Datos cargados correctamente! Filas: {data.shape[0]}, Columnas: {data.shape[1]}")
                        
                        # Mostrar primeras filas
                        st.subheader("Vista previa de los datos")
                        st.dataframe(data.head())
                        
                        # Información de columnas
                        st.subheader("Información de columnas")
                        buffer = []
                        for column in data.columns:
                            buffer.append({
                                "Columna": column,
                                "Tipo": str(data[column].dtype),
                                "Valores únicos": data[column].nunique(),
                                "Valores nulos": data[column].isna().sum()
                            })
                        st.table(pd.DataFrame(buffer))
        else:
            st.warning(f"No se encontraron ligas disponibles para la temporada {temporada_seleccionada}.")
            
    except Exception as e:
        st.error(f"Error al acceder a los datos: {e}")
        st.info("Si el problema persiste, verifica la estructura del repositorio o contacta al desarrollador.")

def cargar_datos_local():
    """Carga datos desde un archivo local."""
    # Opción para cargar archivo local
    uploaded_file = st.file_uploader("Carga tu archivo de datos (CSV, Excel)", 
                                    type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Detectar tipo de archivo
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            # Guardar en la sesión
            st.session_state['data'] = data
            st.session_state['fuente_datos'] = uploaded_file.name
            
            # Mostrar información del dataset
            st.success(f"¡Datos cargados correctamente! Filas: {data.shape[0]}, Columnas: {data.shape[1]}")
            
            # Mostrar primeras filas
            st.subheader("Vista previa de los datos")
            st.dataframe(data.head())
            
            # Información de columnas
            st.subheader("Información de columnas")
            buffer = []
            for column in data.columns:
                buffer.append({
                    "Columna": column,
                    "Tipo": str(data[column].dtype),
                    "Valores únicos": data[column].nunique(),
                    "Valores nulos": data[column].isna().sum()
                })
            st.table(pd.DataFrame(buffer))
            
        except Exception as e:
            st.error(f"Error al cargar los datos: {e}")

def verificar_datos_cargados():
    """Verifica si hay datos cargados y muestra un mensaje si no los hay."""
    if 'data' not in st.session_state or st.session_state['data'] is None:
        st.warning("⚠️ No hay datos cargados. Por favor, ve a la página principal para cargar datos.")
        return False
    return True

def obtener_datos():
    """Obtiene los datos cargados en la sesión."""
    if 'data' in st.session_state:
        return st.session_state['data']
    return None
