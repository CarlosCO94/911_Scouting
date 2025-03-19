import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processing import normalizar_para_radar

def grafico_radar_jugador(data, jugador, categorias, col_nombres):
    """
    Crea un gráfico de radar para un jugador.
    
    Args:
        data (DataFrame): DataFrame con los datos
        jugador (str): Nombre del jugador
        categorias (list): Lista de categorías para el gráfico
        col_nombres (str): Nombre de la columna que contiene los nombres de los jugadores
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    # Preparar datos para el gráfico de radar
    values = data[data[col_nombres] == jugador][categorias].values[0].tolist()
    
    # Crear figura
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
      r=values,
      theta=categorias,
      fill='toself',
      name=jugador
    ))
    
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
        )),
      showlegend=True
    )
    
    return fig

def grafico_comparacion_barras(comp_data, jugador1, jugador2):
    """
    Crea un gráfico de barras para comparar dos jugadores.
    
    Args:
        comp_data (DataFrame): DataFrame con datos comparativos
        jugador1 (str): Nombre del primer jugador
        jugador2 (str): Nombre del segundo jugador
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    # Convertir a formato largo para Plotly
    comp_long = pd.melt(comp_data, id_vars=['Métrica'], 
                       value_vars=[jugador1, jugador2],
                       var_name='Jugador', value_name='Valor')
    
    # Crear gráfico de barras
    fig = px.bar(comp_long, x='Métrica', y='Valor', color='Jugador',
                barmode='group', title=f"Comparación entre {jugador1} y {jugador2}")
    
    return fig

def grafico_radar_comparacion(comp_data, jugador1, jugador2):
    """
    Crea un gráfico de radar para comparar dos jugadores.
    
    Args:
        comp_data (DataFrame): DataFrame con datos comparativos
        jugador1 (str): Nombre del primer jugador
        jugador2 (str): Nombre del segundo jugador
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    # Normalizar valores para el radar chart
    radar_data = normalizar_para_radar(comp_data, jugador1, jugador2)
    
    # Crear figura
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
      r=radar_data[jugador1],
      theta=radar_data['Métrica'],
      fill='toself',
      name=jugador1
    ))
    
    fig.add_trace(go.Scatterpolar(
      r=radar_data[jugador2],
      theta=radar_data['Métrica'],
      fill='toself',
      name=jugador2
    ))
    
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 1]
        )),
      showlegend=True
    )
    
    return fig

def grafico_percentiles_barras(percentiles_df):
    """
    Crea un gráfico de barras para visualizar percentiles.
    
    Args:
        percentiles_df (DataFrame): DataFrame con los percentiles
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    fig = px.bar(percentiles_df, x='Métrica', y='Percentil', 
                title=f"Percentiles",
                color='Percentil', color_continuous_scale='RdYlGn',
                labels={'Percentil': 'Percentil (%)'})
    
    # Añadir líneas de referencia
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=50,
        x1=len(percentiles_df)-0.5,
        y1=50,
        line=dict(color="yellow", width=2, dash="dash"),
    )
    
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=80,
        x1=len(percentiles_df)-0.5,
        y1=80,
        line=dict(color="green", width=2, dash="dash"),
    )
    
    return fig

def grafico_distribucion_metrica(data, metrica, valor_jugador, jugador):
    """
    Crea un histograma para visualizar la distribución de una métrica.
    
    Args:
        data (DataFrame): DataFrame con los datos
        metrica (str): Nombre de la métrica
        valor_jugador (float): Valor del jugador para la métrica
        jugador (str): Nombre del jugador
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    fig = px.histogram(data, x=metrica, nbins=30,
                      title=f"Distribución de {metrica}")
    
    # Añadir línea vertical para el jugador seleccionado
    fig.add_vline(x=valor_jugador, line_width=3, line_dash="dash", line_color="red",
                 annotation_text=f"{jugador}: {valor_jugador}", 
                 annotation_position="top right")
    
    return fig

def grafico_similitud_barras(similarity_df, jugador_ref):
    """
    Crea un gráfico de barras para visualizar la similitud entre jugadores.
    
    Args:
        similarity_df (DataFrame): DataFrame con los datos de similitud
        jugador_ref (str): Nombre del jugador de referencia
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    fig = px.bar(similarity_df, x='Jugador', y='Similitud', 
                title=f"Similitud con {jugador_ref}",
                color='Similitud', color_continuous_scale='Viridis')
    
    return fig

def grafico_radar_perfil(categories, values, jugador):
    """
    Crea un gráfico de radar para visualizar el perfil de un jugador.
    
    Args:
        categories (list): Lista de categorías para el gráfico
        values (list): Lista de valores normalizados
        jugador (str): Nombre del jugador
        
    Returns:
        Figure: Objeto de figura Plotly
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
      r=values,
      theta=categories,
      fill='toself',
      name=jugador
    ))
    
    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 1]
        )),
      showlegend=True
    )
    
    return fig
