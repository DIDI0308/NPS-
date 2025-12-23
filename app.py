import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS CD EL ALTO Dashboard", layout="wide")

# Estilo para fondo negro, franja amarilla y logos
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    
    /* Franja Amarilla Superior */
    .header-banner {
        background-color: #FFFF00;
        padding: 10px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .header-title {
        color: black !important;
        font-family: 'Arial Black', sans-serif;
        font-size: 28px;
        margin: 0;
        text-align: center;
        flex-grow: 1;
    }
    .logo-img {
        height: 70px; /* Ajusta el tamaño de tus logos aquí */
    }

    /* Estilo para el botón de actualización */
    div.stButton > button {
        background-color: #FFFF00;
        color: black;
        border: None;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #e6e600;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO CON LOGOS LOCALES ---
# Nota: Asegúrate de que logo.png y logo2.png estén en la misma carpeta que este script.
import base64

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_logo_izq = get_base64_image("logo2.png")
img_logo_der = get_base64_image("logo.png")

st.markdown(f"""
    <div class="header-banner">
        <img src="data:image/png;base64,{img_logo_izq}" class="logo-img">
        <h1 class="header-title">MONTHLY EVOLUTION</h1>
        <img src="data:image/png;base64,{img_logo_der}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

# Botón de actualización
col_btn, _ = st.columns([1, 5])
with col_btn:
    if st.button("ACTUALIZAR DATOS"):
        st.rerun()

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
    # --- PROCESAMIENTO DE DATOS ---
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    y25_line = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    bgt_line = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    y24_line = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

    val_25 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_bu = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_24 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')
    
    label_25 = str(df_raw.iloc[2, 1]); label_bu = str(df_raw.iloc[3, 1]); label_24 = str(df_raw.iloc[4, 1])

    # Título dinámico interno (Debajo del banner)
    valid_data_2025 = [i for i, v in enumerate(y25_line) if pd.notnull(v) and v != 0]
    last_idx = valid_data_2025[-1] if valid_data_2025 else 0
    mes_actual_nombre = meses[last_idx]
    v_a_25 = int(y25_line[last_idx]) if pd.notnull(y25_line[last_idx]) else 0
    v_a_24 = int(y24_line[last_idx]) if pd.notnull(y24_line[last_idx]) else 0
    v_a_bu = int(bgt_line[last_idx]) if pd.notnull(bgt_line[last_idx]) else 0
    y25_i = int(val_25); ybu_i = int(val_bu)
    p25 = ((val_25 / val_bu) - 1) * 100 if val_bu != 0 else 0
    p24 = ((val_24 / val_bu) - 1) * 100 if val_bu != 0 else 0

    st.markdown(f"""<h2 style='text-align: center; color: #FFFF00; padding-bottom: 10px; font-size: 20px;'>
        NPS CD EL ALTO | {v_a_25} {mes_actual_nombre} – {v_a_24} LY {v_a_bu} BGT (YTD BU) | {y25_i} YTD vs {ybu_i} BGT YTD</h2>""", unsafe_allow_html=True)

    # --- RENDERIZADO DE GRÁFICAS ---
    col_evol, col_ytd = st.columns([3, 1.2])

    with col_evol:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses, y=y25_line, mode='lines+markers+text', name=label_25, line=dict(color='#FFFF00', width=4), text=y25_line, textposition="top center", textfont=dict(color="white")))
        fig_line.add_trace(go.Scatter(x=meses, y=bgt_line, mode='lines', name=label_bu, line=dict(color='#FFD700', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses, y=y24_line, mode='lines+markers+text', name=label_24, line=dict(color='#F4D03F', width=2), text=y24_line, textposition="bottom center", textfont=dict(color="white")))
        fig_line.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False), legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")), height=400)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_ytd:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=[label_24, label_bu, label_25], y=[val_24, val_bu, val_25], text=[f"{val_24}", f"{val_bu}", f"{val_25}"], textposition='auto', marker_color=['#F4D03F', '#FFD700', '#FFFF00'], width=0.6, textfont=dict(color="black", size=14, family="Arial Black")))
        y_top = max(val_25, val_bu, val_24) + 12
        fig_bar.add_shape(type="path", path=f"M 1,{val_bu} L 1,{y_top} L 2,{y_top} L 2,{val_25}", line=dict(color="white", width=2))
        fig_bar.add_shape(type="path", path=f"M 1,{val_bu} L 1,{y_top} L 0,{y_top} L 0,{val_24}", line=dict(color="white", width=2))
        fig_bar.add_annotation(x=1.5, y=y_top, text=f"<b>{p25:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p25 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)
        fig_bar.add_annotation(x=0.5, y=y_top, text=f"<b>{p24:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p24 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)
        fig_bar.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False, range=[0, y_top + 15]), height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- CUADROS EDITABLES INFERIORES ---
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.text_area("Causas Raíz YTD", height=200, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App\n• Precios\n• Puntos")
    with c2: st.text_area("Plan de Acción", height=200, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.\n• Comunicación clientes-ventas.")
    with c3: st.text_area("Key KPIs", height=200, value="• Canjes\n• Rechazo\n• On time\n• In full")
