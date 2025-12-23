import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Monthly Evolution", layout="wide")
st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# --- CONEXIÓN DINÁMICA A GOOGLE SHEETS ---
@st.cache_data(ttl=60)  # Se actualiza cada 60 segundos
def load_sheet_data(spreadsheet_url):
    try:
        # Exportamos la Hoja 1 (gid=0) como CSV
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leemos el CSV y limpiamos nombres de columnas
        df = pd.read_csv(StringIO(response.text))
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# URL de tu archivo
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO DE DATOS ---
df_raw = load_sheet_data(SHEET_URL)

if not df_raw.empty:
    # Definimos los meses y extraemos las filas correspondientes según tu estructura
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # Extraemos los datos reales del Sheet
    # Fila 0: YTD 2025 | Fila 1: YTD BU | Fila 2: YTD 2024
    ytd_2025 = df_raw.iloc[0][meses].tolist()
    ytd_bu = df_raw.iloc[1][meses].tolist()
    ytd_2024 = df_raw.iloc[2][meses].tolist()
    
    # Datos para las barras YTD (columna 'YTD')
    val_ytd_25 = df_raw.iloc[0]['YTD']
    val_ytd_bu = df_raw.iloc[1]['YTD']
    val_ytd_24 = df_raw.iloc[2]['YTD']

    # --- DISEÑO DE INTERFAZ ---
    col_main, col_side = st.columns([3, 1])

    # 1. Gráfica de Líneas (Evolución Mensual)
    with col_main:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2025, mode='lines+markers+text', name='YTD 2025',
                                     line=dict(color='#005587', width=3), text=ytd_2025, textposition="top center"))
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_bu, mode='lines', name='BGT',
                                     line=dict(color='#006A4D', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2024, mode='lines+markers+text', name='YTD 2024',
                                     line=dict(color='#E87722', width=3), text=ytd_2024, textposition="bottom center"))

        fig_line.update_layout(title="NPS MONTHLY EVOLUTION", paper_bgcolor='black', plot_bgcolor='black', 
                              font=dict(color="white"), xaxis=dict(showgrid=False), yaxis=dict(visible=False))
        st.plotly_chart(fig_line, use_container_width=True)

    # 2. Gráfica de Barras (Comparativo YTD)
    with col_side:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=['YTD 2024', 'BGT', 'YTD 2025'], y=[val_ytd_24, val_ytd_bu, val_ytd_25], 
                                 marker_color=['#E87722', '#006A4D', '#005587'], 
                                 text=[val_ytd_24, val_ytd_bu, val_ytd_25], textposition='auto'))
        
        fig_bar.update_layout(title="YTD PERFORMANCE", paper_bgcolor='black', plot_bgcolor='black', 
                              font=dict(color="white"), yaxis=dict(visible=False))
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("No se detectaron datos. Asegúrate de que el Google Sheet tenga permisos de lectura.")
