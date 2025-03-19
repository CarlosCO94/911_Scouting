import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def calcular_percentiles(data, jugador, metricas, col_nombres):
    """
    Calcula los percentiles de un jugador para las métricas seleccionadas.
    
    Args:
        data (DataFrame): DataFrame con los datos
        jugador (str): Nombre del jugador
        metricas (list): Lista de métricas para calcular percentiles
        col_nombres (str): Nombre de la columna que contiene los nombres de los jugadores
        
    Returns:
        DataFrame: DataFrame con los percentiles calculados
    """
    percentiles_list = []
    
    for metrica in metricas:
        valor_jugador = data[data[col_nombres] == jugador][metrica].values[0]
        percentil = (data[metrica] <= valor_jugador).mean() * 100
        
        percentiles_list.append({
            'Métrica': metrica,
            'Valor': valor_jugador,
            'Percentil': percentil,
            'Color': 'green' if percentil >= 80 else ('yellow' if percentil >= 50 else 'red')
        })
    
    # Crear DataFrame de percentiles
    return pd.DataFrame(percentiles_list)

def encontrar_jugadores_similares(data, jugador_ref, features, num_similares, col_nombres):
    """
    Encuentra jugadores similares basados en las características seleccionadas.
    
    Args:
        data (DataFrame): DataFrame con los datos
        jugador_ref (str): Nombre del jugador de referencia
        features (list): Lista de características para calcular la similitud
        num_similares (int): Número de jugadores similares a retornar
        col_nombres (str): Nombre de la columna que contiene los nombres de los jugadores
        
    Returns:
        DataFrame: DataFrame con los jugadores más similares
    """
    # Crear copia de los datos para no modificar los originales
    similarity_data = data.copy()
    
    # Normalizar características
    scaler = StandardScaler()
    similarity_data[features] = scaler.fit_transform(similarity_data[features])
    
    # Obtener vector del jugador de referencia
    player_vector = similarity_data[similarity_data[col_nombres] == jugador_ref][features].values.reshape(1, -1)
    
    # Calcular similitud con todos los demás jugadores
    similarity_scores = []
    
    for idx, row in similarity_data.iterrows():
        if row[col_nombres] != jugador_ref:
            vector = row[features].values.reshape(1, -1)
            similarity = cosine_similarity(player_vector, vector)[0][0]
            similarity_scores.append({
                'Jugador': row[col_nombres],
                'Similitud': similarity
            })
    
    # Ordenar por similitud (mayor a menor)
    similarity_df = pd.DataFrame(similarity_scores).sort_values('Similitud', ascending=False)
    
    # Retornar los N jugadores más similares
    return similarity_df.head(num_similares).reset_index(drop=True)

def identificar_fortalezas_debilidades(data, jugador, col_nombres, num_cols):
    """
    Identifica fortalezas y debilidades de un jugador basado en percentiles.
    
    Args:
        data (DataFrame): DataFrame con los datos
        jugador (str): Nombre del jugador
        col_nombres (str): Nombre de la columna que contiene los nombres de los jugadores
        num_cols (list): Lista de columnas numéricas a considerar
        
    Returns:
        dict: Diccionario con fortalezas, debilidades y percentiles calculados
    """
    # Calcular percentiles para cada métrica
    percentiles = {}
    for col in num_cols:
        valor = data[data[col_nombres] == jugador][col].values[0]
        percentil = (data[col] <= valor).mean() * 100
        percentiles[col] = {
            'valor': valor,
            'percentil': percentil
        }
    
    # Identificar fortalezas (percentil > 80)
    fortalezas = [col for col, info in percentiles.items() if info['percentil'] >= 80]
    
    # Identificar debilidades (percentil < 20)
    debilidades = [col for col, info in percentiles.items() if info['percentil'] <= 20]
    
    # Calcular percentil promedio
    promedio_percentil = sum([info['percentil'] for info in percentiles.values()]) / len(percentiles)
    
    return {
        'fortalezas': fortalezas,
        'debilidades': debilidades,
        'percentiles': percentiles,
        'promedio_percentil': promedio_percentil
    }

def comparar_jugadores_datos(data, jugador1, jugador2, metricas, col_nombres):
    """
    Compara dos jugadores en base a métricas seleccionadas.
    
    Args:
        data (DataFrame): DataFrame con los datos
        jugador1 (str): Nombre del primer jugador
        jugador2 (str): Nombre del segundo jugador
        metricas (list): Lista de métricas para comparar
        col_nombres (str): Nombre de la columna que contiene los nombres de los jugadores
        
    Returns:
        DataFrame: DataFrame con la comparación
    """
    # Obtener datos de ambos jugadores
    datos_j1 = data[data[col_nombres] == jugador1]
    datos_j2 = data[data[col_nombres] == jugador2]
    
    # Crear tabla comparativa
    comp_table = pd.DataFrame({
        'Métrica': metricas,
        jugador1: [datos_j1[m].values[0] for m in metricas],
        jugador2: [datos_j2[m].values[0] for m in metricas],
        'Diferencia': [datos_j1[m].values[0] - datos_j2[m].values[0] for m in metricas],
        'Diferencia (%)': [((datos_j1[m].values[0] / datos_j2[m].values[0]) - 1) * 100 
                         if datos_j2[m].values[0] != 0 else float('inf') 
                         for m in metricas]
    })
    
    return comp_table

def normalizar_para_radar(comp_data, jugador1, jugador2):
    """
    Normaliza datos para gráfico de radar.
    
    Args:
        comp_data (DataFrame): DataFrame con datos comparativos
        jugador1 (str): Nombre del primer jugador
        jugador2 (str): Nombre del segundo jugador
        
    Returns:
        DataFrame: DataFrame con valores normalizados
    """
    radar_data = comp_data.copy()
    
    # Obtener las métricas (primera columna)
    metricas = radar_data['Métrica']
    
    # Para cada métrica, normalizar valores
    for idx, m in enumerate(metricas):
        max_val = max(radar_data[jugador1].iloc[idx], radar_data[jugador2].iloc[idx])
        if max_val > 0:
            radar_data.at[idx, jugador1] = radar_data[jugador1].iloc[idx] / max_val
            radar_data.at[idx, jugador2] = radar_data[jugador2].iloc[idx] / max_val
    
    return radar_data
