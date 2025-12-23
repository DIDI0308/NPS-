import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard Yellow", layout="wide")

# Fondo negro global
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS EN TIEMPO REAL (SIN CACHÉ) ---
def load_live_data(spreadsheet_url):
    try:
        base_url = spreadsheet_url.split('/edit')[0]
        # Forzamos la descarga del CSV y evitamos el caché de red con un timestamp
        csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leemos sin encabezados para usar índices exactos de celdas
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO ---
df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # 1. DATOS GRÁFICA DE LÍNEAS (Filas 3-5, Columnas D-O -> Indices [2-4, 3-14])
    ytd_2025_line = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    bgt_line = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    ytd_2024_line = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()
    
    # 2. DATOS BARRAS DELGADAS (Nombres Col B, Valores Col C -> Indices [2-4, 1-2])
    # Ordenamos para que aparezca 2024, BGT, 2025 de izquierda a derecha
    labels_bar = [df_raw.iloc[4, 1], df_raw.iloc[3, 1], df_raw.iloc[2, 1]]
    values_bar = [
        pd.to_numeric(df_raw.iloc[4, 2], errors='coerce'),
        pd.to_numeric(df_raw.iloc[3, 2], errors='coerce'),
        pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    ]

    # --- DISEÑO EN COLUMNAS ---
    col_evol, col_ytd = st.columns([3, 1]) # 75% Líneas, 25% Barras

    # --- COLUMNA IZQUIERDA: NPS MONTHLY EVOLUTION ---
    with col_evol:
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>NPS MONTHLY EVOLUTION</h3>", unsafe_allow_html=True)
        fig_line = go.Figure()

        # Línea 2025 (Amarillo Brillante)
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2025_line, mode='lines+markers+text', name='YTD 2025',
                                     line=dict(color='#FFFF00', width=4), text=ytd_2025_line, 
                                     textposition="top center", textfont=dict(color="white")))
        # BGT (Dashed)
        fig_line.add_trace(go.Scatter(x=meses, y=bgt_line, mode='lines', name='BGT',
                                     line=dict(color='#FFD700', width=2, dash='dash')))
        # Línea 2024 (Amarillo Ámbar)
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2024_line, mode='lines+markers+text', name='YTD 2024',
                                     line=dict(color='#F4D03F', width=3), text=ytd_2024_line, 
                                     textposition="bottom center", textfont=dict(color="white")))

        fig_line.update_layout(
            paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
            xaxis=dict(showgrid=False, tickfont=dict(color="white")),
            yaxis=dict(visible=False),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
            height=500, margin=dict(t=80, b=40)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # --- COLUMNA DERECHA: BARRAS YTD (B3-B5, C3-C5) ---
    with col_ytd:
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>YTD</h3>", unsafe_allow_html=True)
        fig_bar = go.Figure()

        fig_bar.add_trace(go.Bar(
            x=labels_bar,
            y=values_bar,
            text=values_bar,
            textposition='auto',
            marker_color=['#F4D03F', '#FFD700', '#FFFF00'],
            width=0.4, # Hace las barritas más delgadas
            textfont=dict(color="white", size=14)
        ))

        fig_bar.update_layout(
            paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
            xaxis=dict(tickfont=dict(color="white", size=12), showgrid=False),
            yaxis=dict(visible=False),
            height=500, margin=dict(t=80, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Botón de actualización
    st.button("🔄 ACTUALIZAR DATOS")

else:
    st.info("Esperando conexión con Google Sheets...")
