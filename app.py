import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import os
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS CD EL ALTO Dashboard", layout="wide")

# Estilos CSS
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
    
    .section-banner {
        background-color: #FFFF00;
        color: black !important;
        padding: 4px 10px;
        border-radius: 5px;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 15px;
        font-weight: bold;
    }
    
    .logo-img { height: 70px; }
    
    div.stButton > button {
        background-color: #FFFF00;
        color: black;
        border: None;
        font-weight: bold;
    }
    
    /* TÍTULOS DE RECUADROS: MÁS GRANDES Y CON BORDE */
    .stTextArea label {
        color: #FFFF00 !important;
        font-size: 22px !important; /* Aumentado de 18px a 22px */
        font-weight: bold !important;
        border: 2px solid #FFFF00 !important; /* Borde amarillo añadido */
        padding: 5px 15px !important;
        border-radius: 5px !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
    }

    .detractores-table {
        width: 100%;
        border-collapse: collapse;
        color: black;
        background-color: white;
        margin-bottom: 20px;
    }
    .detractores-table th {
        background-color: #1a3a4a;
        color: white;
        padding: 10px;
        border: 1px solid #ddd;
        font-size: 12px;
    }
    .detractores-table td {
        padding: 8px;
        border: 1px solid #ddd;
        text-align: center;
        font-size: 12px;
        color: black;
    }
    .detractores-table .text-col {
        text-align: left;
        background-color: #f9f9f9;
        width: 25%;
        font-weight: bold;
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

st.markdown(f"""
    <div class="header-banner">
        <img src="data:image/png;base64,{img_logo_izq}" class="logo-img">
        <h1 class="header-title">MONTHLY EVOLUTION</h1>
        <img src="data:image/png;base64,{img_logo_der}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

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
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    y25_m = pd.to_numeric(df.iloc[row_start_idx, 3:15], errors='coerce').tolist()
    bu_m = pd.to_numeric(df.iloc[row_start_idx + 1, 3:15], errors='coerce').tolist()
    y24_m = pd.to_numeric(df.iloc[row_start_idx + 2, 3:15], errors='coerce').tolist()
    val_ytd_25 = pd.to_numeric(df.iloc[row_start_idx, 2], errors='coerce')
    val_ytd_bu = pd.to_numeric(df.iloc[row_start_idx + 1, 2], errors='coerce')
    val_ytd_24 = pd.to_numeric(df.iloc[row_start_idx + 2, 2], errors='coerce')
    
    valid_data = [i for i, v in enumerate(y25_m) if pd.notnull(v) and v != 0]
    last_idx = valid_data[-1] if valid_data else 0
    mes_txt = meses[last_idx]
    
    st.markdown(f"""<div class="section-banner"><h2 style='color: black; margin: 0; font-size: 19px;'>
                {title_prefix} | {int(y25_m[last_idx])} {mes_txt} – {int(y24_m[last_idx])} LY {int(bu_m[last_idx])} BGT ({int(val_ytd_bu)}) | {int(val_ytd_25)} YTD vs {int(val_ytd_bu)} BGT YTD</h2></div>""", unsafe_allow_html=True)

    all_vals = [x for x in (y25_m + bu_m + y24_m) if pd.notnull(x)]
    max_l = max(all_vals) if all_vals else 100; min_l = min(all_vals) if all_vals else 0
    col_a, col_b = st.columns([3, 1.2])
    with col_a:
        fig_l = go.Figure()
        fig_l.add_trace(go.Scatter(x=meses, y=y25_m, mode='markers+lines+text', line=dict(color='#FFFF00', width=4), text=y25_m, textposition="top center", textfont=dict(color="white")))
        fig_l.add_trace(go.Scatter(x=meses, y=bu_m, mode='lines', line=dict(color='#FFD700', width=2, dash='dash')))
        fig_l.add_trace(go.Scatter(x=meses, y=y24_m, mode='markers+lines+text', line=dict(color='#F4D03F', width=2), text=y24_m, textposition="bottom center", textfont=dict(color="white")))
        fig_l.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False), yaxis=dict(visible=False, range=[min_l - 15, max_l + 25]), height=500)
        st.plotly_chart(fig_l, use_container_width=True)
    with col_b:
        fig_b = go.Figure()
        fig_b.add_trace(go.Bar(x=["LY", "BGT", "ACTUAL"], y=[val_ytd_24, val_ytd_bu, val_ytd_25], text=[int(val_ytd_24), int(val_ytd_bu), int(val_ytd_25)], textposition='auto', marker_color=['#F4D03F', '#FFD700', '#FFFF00']))
        fig_b.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), yaxis=dict(visible=False), height=500)
        st.plotly_chart(fig_b, use_container_width=True)

if not df_raw.empty:
    render_nps_block(df_raw, 2, "NPS CD EL ALTO")
    render_nps_block(df_raw, 7, "NPS EA")
    render_nps_block(df_raw, 11, "NPS LP")

    st.markdown('<div class="section-banner">DETRACTORS </div>', unsafe_allow_html=True)
    rows_det = [18, 20, 22]
    months = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    table_html = '<table class="detractores-table"><thead><tr><th>Secondary Driver</th>'
    for m in months: table_html += f'<th>{m}</th>'
    table_html += '</tr></thead><tbody>'
    for r in rows_det:
        text_desc = str(df_raw.iloc[r, 0])
        table_html += f'<tr><td class="text-col">{text_desc}</td>'
        for c in range(3, 15):
            val = df_raw.iloc[r, c]
            table_html += f'<td>{val if pd.notnull(val) else "-"}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    col_a1, col_a2, col_a3 = st.columns(3)
    indices_ytd = [18, 20, 22]

    for idx, col in zip(indices_ytd, [col_a1, col_a2, col_a3]):
        valor_ytd = df_raw.iloc[idx, 2]
        texto_original = str(df_raw.iloc[idx, 0])
        palabras = texto_original.split()
        mitad = len(palabras) // 2
        texto_formateado = "<br>".join([" ".join(palabras[:mitad]), " ".join(palabras[mitad:])])
        
        fig_ring = go.Figure(go.Pie(values=[1], hole=0.8, marker=dict(colors=['rgba(0,0,0,0)'], line=dict(color='#FFFF00', width=6)), showlegend=False, hoverinfo='none'))
        fig_ring.add_annotation(text=f"<b>{valor_ytd}</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="white", size=45, family="Arial Black"))
        fig_ring.add_annotation(text=f"<b>{texto_formateado}</b>", x=0.5, y=-0.25, showarrow=False, font=dict(color="white", size=14), align='center', xref="paper", yref="paper")
        fig_ring.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=100, l=10, r=10), height=320)
        col.plotly_chart(fig_ring, use_container_width=True)

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío (SALES)\n• Servicio de Entrega (LOG)\n• Bees App (SALES)")
    with c2: st.text_area("Plan de Acción", height=150, value="• Se recapacitó en atención al cliente a distribución.\n• Reforzar con Operadores Logísticos.")
    with c3: st.text_area("Key KPI'S", height=150, value="• Canjes\n• Rechazo\n• On time")
