import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap
from io import StringIO
import requests
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# --- FUNCIONES DE UTILIDAD ---
def get_base64(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return None
    return None

# --- MANEJO DE ESTADO DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

# ==========================================
# VISTA 1: HOME
# ==========================================
if st.session_state.page == "home":
    bin_str = get_base64('logo3.png')
    style_home = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str if bin_str else ""}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        overflow: hidden; 
        height: 100vh;
        width: 100vw;
    }}
    header {{visibility: hidden;}}
    .block-container {{padding: 0 !important;}}
    .main-title {{
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        color: white; font-size: 4rem; font-weight: 800;
        text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        z-index: 1000; letter-spacing: 2px;
    }}
    .stHorizontalBlock {{
        position: fixed;
        bottom: 10%; left: 50%;
        transform: translateX(-50%);
        width: 50% !important;
        z-index: 1001;
    }}
    div.stButton > button {{
        background-color: #FFFF00 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }}
    </style>
    '''
    st.markdown(style_home, unsafe_allow_html=True)
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.page = "monthly"
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

# ==========================================
# VISTA 2: CURRENT MONTH (DASHBOARD ORIGINAL)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; overflow: auto !important; }
        div[data-testid="stButton"] button { background-color: #FFFF00 !important; color: #000000 !important; font-weight: bold !important; }
        .banner-amarillo { background-color: #FFFF00; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 25px; }
        .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; color: black; }
        .card-transparent { background-color: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 10px; margin-bottom: 20px; }
        .emoji-solid-yellow { font-size: 110px; text-align: center; color: #FFFF00; }
        label { color: #FFFF00 !important; font-weight: bold !important; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    @st.cache_data
    def load_data_local():
        try:
            df = pd.read_excel('Base bruta dic.xlsx')
            df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
            return df
        except: return pd.DataFrame()

    df = load_data_local()
    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        # Aquí iría el resto de tu lógica de gráficas de la vista 2 (Pie, Lineas, etc.)
        st.info("Vista de Mes Actual cargada con éxito.")
    else:
        st.warning("Archivo 'Base bruta dic.xlsx' no encontrado.")

# ==========================================
# VISTA 3: MONTHLY EVOLUTION (NPS CD EL ALTO)
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("""
        <style>
        .stApp { background-color: black; color: white; }
        .header-banner { background-color: #FFFF00; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 10px; }
        .header-title { color: black !important; font-family: 'Arial Black', sans-serif; font-size: 28px; margin: 0; text-align: center; flex-grow: 1; }
        .section-banner { background-color: #FFFF00; color: black !important; padding: 4px 10px; border-radius: 5px; text-align: center; margin-top: 15px; margin-bottom: 15px; font-weight: bold; }
        .logo-img { height: 70px; }
        div.stButton > button { background-color: #FFFF00 !important; color: black !important; border: None !important; font-weight: bold !important; }
        .stTextArea label { color: #FFFF00 !important; font-size: 22px !important; font-weight: bold !important; border: 2px solid #FFFF00; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
        .detractores-table { width: 100%; border-collapse: collapse; color: black; background-color: white; margin-bottom: 20px; }
        .detractores-table th { background-color: #1a3a4a; color: white; padding: 10px; border: 1px solid #ddd; font-size: 12px; }
        .detractores-table td { padding: 8px; border: 1px solid #ddd; text-align: center; font-size: 12px; color: black; }
        .detractores-table .text-col { text-align: left; background-color: #f9f9f9; width: 25%; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    img_logo_izq = get_base64('logo2.png')
    img_logo_der = get_base64('logo.png')

    st.markdown(f"""
        <div class="header-banner">
            <img src="data:image/png;base64,{img_logo_izq if img_logo_izq else ""}" class="logo-img">
            <h1 class="header-title">MONTHLY EVOLUTION</h1>
            <img src="data:image/png;base64,{img_logo_der if img_logo_der else ""}" class="logo-img">
        </div>
        """, unsafe_allow_html=True)

    def load_live_data(spreadsheet_url):
        try:
            base_url = spreadsheet_url.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
            response = requests.get(csv_url)
            df = pd.read_csv(StringIO(response.text), header=None)
            return df
        except: return pd.DataFrame()

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
        
        col_a, col_b = st.columns([3, 1.2])
        with col_a:
            fig_l = go.Figure()
            fig_l.add_trace(go.Scatter(x=meses, y=y25_m, mode='markers+lines+text', name="2025", line=dict(color='#FFFF00', width=4), text=y25_m, textposition="top center", textfont=dict(color="white")))
            fig_l.add_trace(go.Scatter(x=meses, y=bu_m, mode='lines', name="Budget", line=dict(color='#FFD700', width=2, dash='dash')))
            fig_l.add_trace(go.Scatter(x=meses, y=y24_m, mode='markers+lines+text', name="2024", line=dict(color='#F4D03F', width=2), text=y24_m, textposition="bottom center", textfont=dict(color="white")))
            fig_l.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=500)
            st.plotly_chart(fig_l, use_container_width=True)
        with col_b:
            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(x=["2024", "Budget", "2025"], y=[val_ytd_24, val_ytd_bu, val_ytd_25], marker_color=['#F4D03F', '#FFD700', '#FFFF00']))
            fig_b.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=500)
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

        # --- ANILLOS AMARILLOS ---
        col_a1, col_a2, col_a3 = st.columns(3)
        indices_ytd = [18, 20, 22]
        for idx, col in zip(indices_ytd, [col_a1, col_a2, col_a3]):
            valor_ytd = df_raw.iloc[idx, 2]
            texto_original = str(df_raw.iloc[idx, 0])
            palabras = texto_original.split()
            mitad = len(palabras) // 2
            texto_formateado = "<br>".join([" ".join(palabras[:mitad]), " ".join(palabras[mitad:])])
            fig_ring = go.Figure(go.Pie(values=[1], hole=0.8, marker=dict(colors=['rgba(0,0,0,0)'], line=dict(color='#FFFF00', width=6)), showlegend=False))
            fig_ring.add_annotation(text=f"<b>{valor_ytd}</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="white", size=45))
            fig_ring.add_annotation(text=f"<b>{texto_formateado}</b>", x=0.5, y=-0.25, showarrow=False, font=dict(color="white", size=14))
            fig_ring.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=100, l=10, r=10), height=320)
            col.plotly_chart(fig_ring, use_container_width=True)

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App")
        with c2: st.text_area("Plan de Acción", height=150, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.")
        with c3: st.text_area("Key KPIs", height=150, value="• Canjes\n• Rechazo\n• On time")
