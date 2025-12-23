import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Monthly Evolution", layout="wide")
st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)

# --- CONEXIÓN DINÁMICA A GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def load_nps_data(spreadsheet_url):
    try:
        # Exportamos la Hoja 1 (gid=0) como CSV
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leemos el CSV
        df = pd.read_csv(StringIO(response.text))
        # Limpiamos nombres de columnas (quitar espacios en blanco)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# URL de tu archivo
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

# --- PROCESAMIENTO DE DATOS ---
df_raw = load_nps_data(SHEET_URL)

if not df_raw.empty:
    # Definimos las columnas de los meses
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    # Jalar info por filas según tu especificación:
    # Fila 0 (NPS YTD 2025): [47, 56, 57, 58, 54, 59, 59, 60, 65, 61, 65, 64]
    ytd_2025 = df_raw.iloc[0][meses].values
    val_bar_25 = df_raw.iloc[0]['YTD']

    # Fila 1 (YTD BU / BGT): [54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54, 54]
    ytd_bu = df_raw.iloc[1][meses].values
    val_bar_bu = df_raw.iloc[1]['YTD']

    # Fila 2 (YTD 2024): [40, 32, 50, 57, 45, 46, 47, 49, 53, 49, 45, 55]
    ytd_2024 = df_raw.iloc[2][meses].values
    val_bar_24 = df_raw.iloc[2]['YTD']

    # --- DISEÑO DE INTERFAZ ---
    st.markdown("<h2 style='text-align: center; color: white;'>MONTHLY EVOLUTION PERFORMANCE</h2>", unsafe_allow_html=True)
    
    col_evol, col_ytd = st.columns([3, 1])

    # 1. Gráfica de Líneas (Izquierda)
    with col_evol:
        fig_line = go.Figure()
        
        # YTD 2025 (Azul)
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2025, mode='lines+markers+text', name='YTD 2025',
                                     line=dict(color='#005587', width=3), text=ytd_2025, 
                                     textposition="top center", textfont=dict(color="white")))
        
        # BGT (Verde)
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_bu, mode='lines', name='BGT',
                                     line=dict(color='#006A4D', width=2), textfont=dict(color="white")))
        
        # YTD 2024 (Naranja)
        fig_line.add_trace(go.Scatter(x=meses, y=ytd_2024, mode='lines+markers+text', name='YTD 2024',
                                     line=dict(color='#E87722', width=3), text=ytd_2024, 
                                     textposition="bottom center", textfont=dict(color="white")))

        fig_line.update_layout(
            paper_bgcolor='black', plot_bgcolor='black',
            xaxis=dict(showgrid=False, tickfont=dict(color="white")),
            yaxis=dict(showgrid=True, gridcolor='#333333', visible=False),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
            height=500, margin=dict(l=10, r=10, t=50, b=50)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # 2. Gráfica de Barras (Derecha)
    with col_ytd:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=['YTD 24', 'BGT', 'YTD 25'],
            y=[val_bar_24, val_bar_bu, val_bar_25],
            text=[val_bar_24, val_bar_bu, val_bar_25],
            textposition='auto',
            marker_color=['#E87722', '#006A4D', '#005587'],
            textfont=dict(color="white", size=16)
        ))

        fig_bar.update_layout(
            title=dict(text="YTD", x=0.5, font=dict(color="white", size=18)),
            paper_bgcolor='black', plot_bgcolor='black',
            xaxis=dict(tickfont=dict(color="white")),
            yaxis=dict(visible=False),
            height=500, margin=dict(l=10, r=10, t=80, b=50)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Tabla de Resumen (Inferior)
    st.write("### Detalle Mensual")
    st.dataframe(df_raw.iloc[0:3], use_container_width=True)

else:
    st.error("No se pudieron cargar los datos desde la Hoja 1. Revisa los permisos del enlace.")
