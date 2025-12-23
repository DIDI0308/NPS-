import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS YTD Performance", layout="wide")

# --- ESTILO CSS PARA FONDO NEGRO ---
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def load_nps_data(spreadsheet_url):
    try:
        # Exportamos la Hoja 1 (gid=0) como CSV
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        response = requests.get(csv_url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        # Limpieza de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error de conexión con Google Sheets: {e}")
        return pd.DataFrame()

# URL de tu archivo de Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO DE DATOS ---
df_raw = load_nps_data(SHEET_URL)

if not df_raw.empty:
    # Extracción de valores YTD específicos de las filas 0, 1 y 2
    # Fila 0: YTD 2025 | Fila 1: YTD BU | Fila 2: YTD 2024
    val_ytd_25 = df_raw.iloc[0]['YTD']
    val_ytd_bu = df_raw.iloc[1]['YTD']
    val_ytd_24 = df_raw.iloc[2]['YTD']

    # --- RENDERIZADO DE LA GRÁFICA DE BARRAS YTD ---
    st.markdown("<h2 style='text-align: center; color: white;'>YTD PERFORMANCE COMPARISON</h2>", unsafe_allow_html=True)

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        x=['YTD 2024', 'YTD BU', 'YTD 2025'],
        y=[val_ytd_24, val_ytd_bu, val_ytd_25],
        text=[val_ytd_24, val_ytd_bu, val_ytd_25],
        textposition='auto',
        marker_color=['#E87722', '#006A4D', '#005587'], # Naranja, Verde, Azul
        textfont=dict(color="white", size=20)
    ))

    fig_bar.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color="white"),
        xaxis=dict(
            tickfont=dict(size=16, color="white"),
            showgrid=False
        ),
        yaxis=dict(
            visible=False, # Ocultamos el eje Y para que se vea como en tu imagen
            range=[0, max(val_ytd_25, val_ytd_bu) + 15]
        ),
        height=500,
        margin=dict(t=50, b=50, l=100, r=100)
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABLA DE DATOS INFERIOR ---
    st.markdown("---")
    st.write("### Resumen de Datos Extraídos")
    st.dataframe(df_raw.iloc[0:3][['YTD']], use_container_width=True)

else:
    st.warning("No se pudo cargar la información. Verifica los permisos de tu Google Sheet.")
