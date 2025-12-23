import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import os
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS CD EL ALTO Dashboard", layout="wide")

# Estilos CSS (Fondo negro de app, franja amarilla, títulos de recuadros amarillos)
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
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
    .logo-img { height: 70px; }
    div.stButton > button {
        background-color: #FFFF00;
        color: black;
        border: None;
        font-weight: bold;
    }
    .stTextArea label {
        color: #FFFF00 !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE LOGOS ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

img_logo_izq = get_base64_image("logo2.png")
img_logo_der = get_base64_image("logo.png")

# --- ENCABEZADO PRINCIPAL ---
st.markdown(f"""
    <div class="header-banner">
        <img src="data:image/png;base64,{img_logo_izq}" class="logo-img">
        <h1 class="header-title">MONTHLY EVOLUTION</h1>
        <img src="data:image/png;base64,{img_logo_der}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

# Botón de actualización superior izquierdo
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

SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"
df_raw = load_live_data(SHEET_URL)

def render_nps_block(df, row_start_idx, title_prefix):
    """Función para renderizar bloques con fondo blanco y texto negro"""
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    
    y25_m = pd.to_numeric(df.iloc[row_start_idx, 3:15], errors='coerce').tolist()
    bu_m = pd.to_numeric(df.iloc[row_start_idx + 1, 3:15], errors='coerce').tolist()
    y24_m = pd.to_numeric(df.iloc[row_start_idx + 2, 3:15], errors='coerce').tolist()

    val_ytd_25 = pd.to_numeric(df.iloc[row_start_idx, 2], errors='coerce')
    val_ytd_bu = pd.to_numeric(df.iloc[row_start_idx + 1, 2], errors='coerce')
    val_ytd_24 = pd.to_numeric(df.iloc[row_start_idx + 2, 2], errors='coerce')
    
    label_25 = str(df.iloc[row_start_idx, 1]); label_bu = str(df.iloc[row_start_idx + 1, 1]); label_24 = str(df.iloc[row_start_idx + 2, 1])

    valid_data = [i for i, v in enumerate(y25_m) if pd.notnull(v) and v != 0]
    last_idx = valid_data[-1] if valid_data else 0
    mes_txt = meses[last_idx]
    
    st.markdown(f"""
        <h2 style='text-align: center; color: #FFFF00; padding: 15px 0; font-size: 20px;'>
            {title_prefix} | {int(y25_m[last_idx])} {mes_txt} – {int(y24_m[last_idx])} LY {int(bu_m[last_idx])} BGT ({int(val_ytd_bu)}) | {int(val_ytd_25)} YTD vs {int(val_ytd_bu)} BGT YTD
        </h2>
    """, unsafe_allow_html=True)

    # Cálculo de límites para el eje Y
    all_values_l = [x for x in (y25_m + bu_m + y24_m) if pd.notnull(x)]
    max_val_l = max(all_values_l) if all_values_l else 100
    min_val_l = min(all_values_l) if all_values_l else 0

    col_a, col_b = st.columns([3, 1.2])
    with col_a:
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=meses, y=y25_m, mode='lines+markers+text', name=label_25, line=dict(color='#E6B400', width=4), text=y25_m, textposition="top center", textfont=dict(color="black")))
        fig_l.add_trace(go.Scatter(x=meses, y=bu_m, mode='lines', name=label_bu, line=dict(color='#999999', width=2, dash='dash')))
        fig_l.add_trace(go.Scatter(x=meses, y=y24_m, mode='lines+markers+text', name=label_24, line=dict(color='#F4D03F', width=2), text=y24_m, textposition="bottom center", textfont=dict(color="black")))
        
        fig_l.update_layout(
            paper_bgcolor='white', plot_bgcolor='white', font=dict(color="black"), # Fondo blanco, fuente negra
            xaxis=dict(showgrid=True, gridcolor='lightgray', tickfont=dict(color="black")),
            yaxis=dict(visible=False, range=[min_val_l - 15, max_val_l + 25]),
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center", font=dict(color="black")),
            height=500, margin=dict(t=50, l=20, r=20, b=20)
        )
        st.plotly_chart(fig_l, use_container_width=True)

    with col_b:
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=[label_24, label_bu, label_25], y=[val_ytd_24, val_ytd_bu, val_ytd_25], text=[f"{val_ytd_24}", f"{val_ytd_bu}", f"{val_ytd_25}"], textposition='auto', marker_color=['#F4D03F', '#FFD700', '#E6B400'], width=0.6, textfont=dict(color="black", size=14, family="Arial Black")))
        
        y_t = max(val_ytd_25, val_ytd_bu, val_ytd_24) + 15
        p25 = ((val_ytd_25 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        p24 = ((val_ytd_24 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        
        fig_b.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_t} L 2,{y_t} L 2,{val_ytd_25}", line=dict(color="black", width=2))
        fig_b.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_t} L 0,{y_t} L 0,{val_ytd_24}", line=dict(color="black", width=2))
        
        fig_b.add_annotation(x=1.5, y=y_t, text=f"<b>{p25:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p25 >= 0 else "#FF0000", font=dict(color="white"), bordercolor="black", borderpad=5)
        fig_b.add_annotation(x=0.5, y=y_t, text=f"<b>{p24:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p24 >= 0 else "#FF0000", font=dict(color="white"), bordercolor="black", borderpad=5)
        
        fig_b.update_layout(
            paper_bgcolor='white', plot_bgcolor='white', font=dict(color="black"), # Fondo blanco, fuente negra
            xaxis=dict(showgrid=False, tickfont=dict(color="black")),
            yaxis=dict(visible=False, range=[0, y_t + 30]),
            height=500, margin=dict(t=50, l=20, r=20, b=20)
        )
        st.plotly_chart(fig_b, use_container_width=True)

if not df_raw.empty:
    render_nps_block(df_raw, 2, "NPS CD EL ALTO")
    st.markdown("<br>", unsafe_allow_html=True)
    render_nps_block(df_raw, 7, "NPS CD EL ALTO - SECCIÓN 2")

    # --- CUADROS EDITABLES (Mantienen fondo negro y títulos amarillos) ---
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App")
    with c2: st.text_area("Plan de Acción", height=150, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.")
    with c3: st.text_area("Key KPIs", height=150, value="• Canjes\n• Rechazo\n• On time")
