import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Monthly Evolution", layout="wide")
st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def load_nps_data(spreadsheet_url):
    try:
        # Exportamos la Hoja 1 (gid=0) como CSV
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leer el CSV sin cabeceras para manejar las filas por índice exacto
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO DE DATOS ---
df_raw = load_nps_data(SHEET_URL)

if not df_raw.empty:
    # Definimos los meses para el eje X
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # Índices de columnas D a O son 3 a 14 en Python (0-indexed)
    # Fila 3 (Índice 2): YTD 2025
    ytd_2025 = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    
    # Fila 4 (Índice 3): BGT (Presupuesto)
    bgt_val = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    
    # Fila 5 (Índice 4): YTD 2024
    ytd_2024 = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

    # --- RENDERIZADO DE LA GRÁFICA DE LÍNEAS ---
    st.markdown("<h2 style='text-align: center;'>NPS MONTHLY EVOLUTION</h2>", unsafe_allow_html=True)

    fig = go.Figure()

    # Línea YTD 2025 (Azul)
    fig.add_trace(go.Scatter(
        x=meses, y=ytd_2025, mode='lines+markers+text', name='YTD 2025',
        line=dict(color='#005587', width=4),
        text=ytd_2025, textposition="top center",
        textfont=dict(color="white", size=12)
    ))

    # Línea BGT (Verde)
    fig.add_trace(go.Scatter(
        x=meses, y=bgt_val, mode='lines', name='BGT',
        line=dict(color='#006A4D', width=3, dash='solid'),
        text=[bgt_val[0] if i==0 else "" for i in range(12)], textposition="middle left"
    ))

    # Línea YTD 2024 (Naranja)
    fig.add_trace(go.Scatter(
        x=meses, y=ytd_2024, mode='lines+markers+text', name='YTD 2024',
        line=dict(color='#E87722', width=3),
        text=ytd_2024, textposition="bottom center",
        textfont=dict(color="white", size=12)
    ))

    # Configuración de Layout
    fig.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color="white"),
        xaxis=dict(showgrid=False, tickfont=dict(size=14)),
        yaxis=dict(visible=False, range=[min(ytd_2024+ytd_2025)-5, max(ytd_2024+ytd_2025)+10]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=600,
        margin=dict(l=50, r=50, t=100, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Vista previa técnica para confirmar filas/columnas
    with st.expander("Confirmación de datos extraídos (Filas 3-5, Col D-O)"):
        st.write("Datos YTD 2025:", ytd_2025)
        st.write("Datos BGT:", bgt_val)
        st.write("Datos YTD 2024:", ytd_2024)
else:
    st.warning("No se pudo conectar con el Google Sheet. Verifica los permisos del enlace.")
