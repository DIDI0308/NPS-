import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS YTD Performance", layout="wide")
st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DE DATOS (GOOGLE SHEETS) ---
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
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# URL de tu archivo proporcionado
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO ---
df_raw = load_nps_data(SHEET_URL)

if not df_raw.empty:
    # Definimos columnas de meses
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # Jalar datos por filas según tu estructura:
    # Fila 0: YTD 2025 | Fila 1: YTD BU | Fila 2: YTD 2024
    ytd_2025_val = df_raw.iloc[0]['YTD']
    ytd_bu_val = df_raw.iloc[1]['YTD']
    ytd_2024_val = df_raw.iloc[2]['YTD']

    # --- DISEÑO DE DASHBOARD ---
    st.markdown("<h2 style='text-align: center;'>NPS YTD PERFORMANCE COMPARISON</h2>", unsafe_allow_html=True)

    # 1. Gráfico de Barras Principal (YTD 2025 vs BU vs YTD 2024)
    fig_ytd = go.Figure()

    fig_ytd.add_trace(go.Bar(
        x=['YTD 2024', 'YTD BU (BGT)', 'YTD 2025'],
        y=[ytd_2024_val, ytd_bu_val, ytd_2025_val],
        text=[ytd_2024_val, ytd_bu_val, ytd_2025_val],
        textposition='auto',
        marker_color=['#E87722', '#006A4D', '#005587'], # Naranja, Verde, Azul
        textfont=dict(color="white", size=18)
    ))

    fig_ytd.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color="white"),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(visible=False, range=[0, max(ytd_2025_val, ytd_bu_val) + 15]),
        height=500,
        margin=dict(t=50, b=50)
    )

    st.plotly_chart(fig_ytd, use_container_width=True)

    # 2. Resumen de Métricas en Tarjetas
    m1, m2, m3 = st.columns(3)
    m1.metric(label="YTD 2025", value=ytd_2025_val, delta=f"{ytd_2025_val - ytd_bu_val} vs BGT")
    m2.metric(label="YTD BU (BGT)", value=ytd_bu_val)
    m3.metric(label="YTD 2024", value=ytd_2024_val, delta=f"{ytd_2025_val - ytd_2024_val} vs LY", delta_color="normal")

    # 3. Evolución Mensual Detallada (Líneas)
    st.markdown("---")
    st.markdown("### Monthly Evolution Details")
    
    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(x=meses, y=df_raw.iloc[0][meses], mode='lines+markers+text', name='2025', 
                                  line=dict(color='#005587', width=3), text=df_raw.iloc[0][meses], textposition="top center"))
    fig_evol.add_trace(go.Scatter(x=meses, y=df_raw.iloc[1][meses], mode='lines', name='BGT', 
                                  line=dict(color='#006A4D', width=2, dash='dash')))
    fig_evol.add_trace(go.Scatter(x=meses, y=df_raw.iloc[2][meses], mode='lines+markers', name='2024', 
                                  line=dict(color='#E87722', width=2)))

    fig_evol.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=400,
                          xaxis=dict(showgrid=False), yaxis=dict(visible=False))
    st.plotly_chart(fig_evol, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos. Verifica los permisos de acceso del Google Sheet.")
