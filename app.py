import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS YTD Growth Analysis", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_live_data(spreadsheet_url):
    try:
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
        response = requests.get(csv_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # Extracción de valores de Columna C (Índice 2), Filas 3, 4, 5
    val_2025 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_bgt  = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_2024 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')

    # Cálculos de Crecimiento
    crecimiento_vs_bgt = ((val_2025 / val_bgt) - 1) * 100 if val_bgt != 0 else 0
    distancia_2024_vs_bgt = ((val_2024 / val_bgt) - 1) * 100 if val_bgt != 0 else 0

    col_evol, col_ytd = st.columns([3, 1])

    with col_evol:
        # (Gráfica de líneas omitida en este snippet para foco en barras, pero se mantiene igual)
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>NPS MONTHLY EVOLUTION</h3>", unsafe_allow_html=True)
        # ... (Insertar código de líneas aquí)

    with col_ytd:
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>YTD GROWTH</h3>", unsafe_allow_html=True)
        
        # Etiquetas personalizadas para las barras que muestran el % de crecimiento/caída
        etiquetas_barras = [
            f"{val_2024}%<br>({distancia_2024_vs_bgt:.1f}% vs BU)", # Muestra cuán bajo era el 2024
            f"{val_bgt}%", 
            f"{val_2025}%<br>(+{crecimiento_vs_bgt:.1f}% vs BU)"   # Muestra crecimiento 2025
        ]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=['2024', 'BGT', '2025'],
            y=[val_2024, val_bgt, val_2025],
            text=etiquetas_barras,
            textposition='outside',
            marker_color=['#F4D03F', '#FFD700', '#FFFF00'],
            width=0.45,
            textfont=dict(color="white", size=13)
        ))

        fig_bar.update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color="white"),
            xaxis=dict(tickfont=dict(color="white", size=14), showgrid=False),
            yaxis=dict(visible=False, range=[0, max(val_2025, val_bgt) + 25]), # Espacio para el texto arriba
            height=500,
            margin=dict(t=50, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🔄 ACTUALIZAR DATOS"):
        st.rerun()

else:
    st.info("Conectando con Google Sheets...")
