# Aplicación de Análisis de Jugadores

Esta aplicación de Streamlit permite analizar datos de jugadores de fútbol con múltiples herramientas avanzadas.

## Características

- **Carga de datos** directamente desde GitHub o archivos locales
- **Búsqueda de jugadores** por nombre con visualización de perfiles
- **Comparación entre jugadores** con gráficos y análisis detallados
- **Búsqueda de jugadores similares** mediante análisis de similitud
- **Análisis de percentiles** para entender el rendimiento relativo
- **Generación de informes IA** con recomendaciones personalizadas

## Estructura del proyecto

```
├── Home.py                 # Página principal
├── README.md               # Este archivo
├── config.py               # Configuración global
├── requirements.txt        # Dependencias
├── pages/                  # Páginas de la aplicación
│   ├── __init__.py         # Inicialización del paquete
│   ├── 1_Buscar_Jugador.py # Página de búsqueda
│   ├── 2_Comparar_Jugadores.py # Página de comparación
│   ├── 3_Jugadores_Similares.py # Página de similitud
│   ├── 4_Percentiles.py    # Página de percentiles
│   └── 5_Generar_Informe_IA.py # Página de informes
└── utils/                  # Utilidades
    ├── __init__.py         # Inicialización del paquete
    ├── data_laloader.py    # Carga de datos
    ├── data_processing.py  # Procesamiento de datos
    └── visualization.py    # Funciones de visualización
```

## Instalación

1. Clona este repositorio
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
streamlit run Home.py
```

## Uso

1. En la página principal, carga datos desde GitHub seleccionando la temporada y liga
2. Navega entre las diferentes páginas usando el menú de la barra lateral
3. Sigue las instrucciones en cada página para analizar jugadores

## Fuentes de datos

La aplicación está configurada para acceder a datos de las siguientes ligas:
- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1

Con temporadas desde 2021-2022 hasta 2023-2024.

## Personalización

Puedes personalizar la aplicación modificando los siguientes archivos:
- `config.py`: Configuración global y opciones predeterminadas
- `utils/`: Actualiza las funciones de utilidad para agregar nuevas características

## Requisitos

- Python 3.7+
- Streamlit 1.32.0+
- Pandas, NumPy, Scikit-learn, Plotly

## Contacto

Si tienes alguna pregunta o sugerencia, no dudes en contactar o abrir un issue en GitHub.
