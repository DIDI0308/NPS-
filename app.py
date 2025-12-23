import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Real-Time Evolution", layout="wide")
st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA SIN CACHÉ (Sincronización Total) ---
def load_nps_live_data(spreadsheet_url):
    try:
        # Forzamos la descarga del CSV de la Hoja 1 (gid=0)
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        
        # Agregamos un parámetro aleatorio a la URL para saltar posibles cachés de red
        response = requests.get(csv_url + "&cache_bust=1")
        response.raise_for_status()
        
        # Leemos el CSV sin usar la primera fila como nombres (header=None) 
        # para que la Fila 1 de Sheets sea el índice 0 de Pandas
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de sincronización: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO DE DATOS ---
df_raw = load_nps_live_data(SHEET_URL)

if not df_raw.empty:
    # Eje X: Meses
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # EXTRACCIÓN POR COORDENADAS:
    # Columnas D a O son los índices 3 a 14 en Python.
    
    # Fila 3 de Sheets -> Índice 2 en Pandas (YTD 2025)
    ytd_2025 = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    
    # Fila 4 de Sheets -> Índice 3 en Pandas (BGT)
    bgt_val = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    
    # Fila 5 de Sheets -> Índice 4 en Pandas (YTD 2024)
    ytd_2024 = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

    # --- GRÁFICA ---
    st.markdown("<h2 style='text-align: center;'>NPS MONTHLY EVOLUTION (LIVE)</h2>", unsafe_allow_html=True)

    fig = go.Figure()

    # YTD 2025 (Azul)
    fig.add_trace(go.Scatter(x=meses, y=ytd_2025, mode='lines+markers+text', name='YTD 2025',
                             line=dict(color='#005587', width=4), text=ytd_2025, textposition="top center"))

    # BGT (Verde)
    fig.add_trace(go.Scatter(x=meses, y=bgt_val, mode='lines', name='BGT',
                             line=dict(color='#006A4D', width=3)))

    # YTD 2024 (Naranja)
    fig.add_trace(go.Scatter(x=meses, y=ytd_2024, mode='lines+markers+text', name='YTD 2024',
                             line=dict(color='#E87722', width=3), text=ytd_2024, textposition="bottom center"))

    fig.update_layout(
        paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
        xaxis=dict(showgrid=False), yaxis=dict(visible=False),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # Botón manual de refresco
    if st.button("🔄 Sincronizar ahora"):
        st.rerun()

else:
    st.info("Conectando con Google Sheets...")
