import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Performance Dashboard", layout="wide")

# Estilo Global: Fondo Negro y Texto Blanco
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    button { border-radius: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS EN TIEMPO REAL ---
def load_live_data(spreadsheet_url):
    try:
        base_url = spreadsheet_url.split('/edit')[0]
        # Salto de caché para sincronización inmediata
        csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
        response = requests.get(csv_url)
        response.raise_for_status()
        # Leemos sin encabezados para usar índices: Fila 3=2, Fila 4=3, Fila 5=4
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de conexión con Sheets: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# Ejecución de carga
df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # 1. EXTRACCIÓN DE DATOS PARA LÍNEAS (Filas 3-5, Columnas D-O)
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    y25_line = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    bgt_line = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    y24_line = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

    # 2. EXTRACCIÓN PARA BARRAS (Filas 3-5, Col B y C)
    val_25 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_bu = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_24 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')
    
    label_25 = str(df_raw.iloc[2, 1])
    label_bu = str(df_raw.iloc[3, 1])
    label_24 = str(df_raw.iloc[4, 1])

    # 3. CÁLCULOS DE CRECIMIENTO (%)
    crec_25_vs_bu = ((val_25 / val_bu) - 1) * 100 if val_bu else 0
    caida_24_vs_bu = ((val_24 / val_bu) - 1) * 100 if val_bu else 0

    # --- RENDERIZADO ---
    st.markdown("<h2 style='text-align: center; color: #FFFF00;'>NPS PERFORMANCE EVOLUTION</h2>", unsafe_allow_html=True)

    col_evol, col_ytd = st.columns([3, 1])

    # GRÁFICA DE LÍNEAS (IZQUIERDA)
    with col_evol:
        fig_line = go.Figure()
        
        # YTD 2025
        fig_line.add_trace(go.Scatter(x=meses, y=y25_line, mode='lines+markers+text', name=label_25,
                                     line=dict(color='#FFFF00', width=4), text=y25_line, 
                                     textposition="top center", textfont=dict(color="white")))
        # BUDGET
        fig_line.add_trace(go.Scatter(x=meses, y=bgt_line, mode='lines', name=label_bu,
                                     line=dict(color='#FFD700', width=2, dash='dash')))
        # YTD 2024
        fig_line.add_trace(go.Scatter(x=meses, y=y24_line, mode='lines+markers+text', name=label_24,
                                     line=dict(color='#F4D03F', width=2), text=y24_line, 
                                     textposition="bottom center", textfont=dict(color="white")))

        fig_line.update_layout(
            paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
            xaxis=dict(showgrid=False, tickfont=dict(color="white")),
            yaxis=dict(visible=False),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
            height=500, margin=dict(t=80, b=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # GRÁFICA DE BARRAS (DERECHA)
    with col_ytd:
        # Etiquetas con el análisis de % solicitado
        txt_24 = f"{val_24}%<br>({caida_24_vs_bu:.1f}% vs BU)" # Cuán bajo era el 2024
        txt_bu = f"{val_bu}%"
        txt_25 = f"{val_25}%<br>(+{crec_25_vs_bu:.1f}% vs BU)" # Crecimiento 2025

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=[label_24, label_bu, label_25],
            y=[val_24, val_bu, val_25],
            text=[txt_24, txt_bu, txt_25],
            textposition='outside',
            marker_color=['#F4D03F', '#FFD700', '#FFFF00'],
            width=0.5,
            textfont=dict(color="white", size=12)
        ))

        fig_bar.update_layout(
            title=dict(text="YTD GROWTH", x=0.5, font=dict(color="#FFFF00")),
            paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
            xaxis=dict(tickfont=dict(color="white"), showgrid=False),
            yaxis=dict(visible=False, range=[0, max(val_25, val_bu) + 30]),
            height=500, margin=dict(t=80, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Botón de Sincronización
    if st.button("🔄 ACTUALIZAR DESDE GOOGLE SHEETS"):
        st.rerun()

else:
    st.info("Conectando con la base de datos en Google Sheets...")
