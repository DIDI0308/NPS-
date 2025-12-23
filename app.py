import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard Performance", layout="wide")

# Fondo negro global
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    [data-testid="stMetricValue"] { color: #FFFF00 !important; } /* Números en amarillo */
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS EN TIEMPO REAL ---
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

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # 1. EXTRACCIÓN DE VALORES YTD (Columnas B y C, Filas 3-5)
    # Fila 3: 2025 | Fila 4: BGT | Fila 5: 2024
    val_2025 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_bgt  = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_2024 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')

    # 2. CÁLCULO DE CRECIMIENTO / COMPARATIVAS
    crecimiento_vs_bgt = val_2025 - val_bgt
    brecha_2024_vs_bgt = val_2024 - val_bgt

    # --- INDICADORES SUPERIORES (KPIs) ---
    st.markdown("<h2 style='text-align: center; color: #FFFF00;'>ANÁLISIS DE CRECIMIENTO NPS</h2>", unsafe_allow_html=True)
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric(label="YTD 2025 vs BGT", 
                  value=f"{val_2025}%", 
                  delta=f"{crecimiento_vs_bgt:+.1f} pts vs Meta",
                  delta_color="normal")
    
    with kpi2:
        st.metric(label="BGT (META BU)", 
                  value=f"{val_bgt}%")
    
    with kpi3:
        # Aquí se muestra qué tan bajo fue el 2024 respecto a la meta (BU)
        st.metric(label="YTD 2024 vs BGT", 
                  value=f"{val_2024}%", 
                  delta=f"{brecha_2024_vs_bgt:.1f} pts vs Meta",
                  delta_color="inverse") # Rojo si es muy bajo

    st.markdown("---")

    # --- GRÁFICAS (LÍNEAS Y BARRAS) ---
    col_evol, col_ytd = st.columns([3, 1])

    with col_evol:
        meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        y25_line = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
        bgt_line = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
        y24_line = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses, y=y25_line, mode='lines+markers+text', name='2025',
                                     line=dict(color='#FFFF00', width=4), text=y25_line, 
                                     textposition="top center", textfont=dict(color="white")))
        fig_line.add_trace(go.Scatter(x=meses, y=bgt_line, mode='lines', name='BGT',
                                     line=dict(color='#FFD700', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses, y=y24_line, mode='lines+markers+text', name='2024',
                                     line=dict(color='#F4D03F', width=2), text=y24_line, 
                                     textposition="bottom center", textfont=dict(color="white")))

        fig_line.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False),
                              legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
                              height=450, margin=dict(t=50, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_ytd:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=['2024', 'BGT', '2025'],
            y=[val_2024, val_bgt, val_2025],
            text=[val_2024, val_bgt, val_2025],
            textposition='auto',
            marker_color=['#F4D03F', '#FFD700', '#FFFF00'],
            width=0.4,
            textfont=dict(color="white", size=14)
        ))
        fig_bar.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(tickfont=dict(color="white"), showgrid=False), yaxis=dict(visible=False),
                              height=450, margin=dict(t=50, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🔄 ACTUALIZAR ANALISIS"):
        st.rerun()

else:
    st.info("Sincronizando con Google Sheets...")
