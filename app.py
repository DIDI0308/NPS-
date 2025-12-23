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
        top: 40%; left: 50%;
        transform: translate(-50%, -50%);
        color: white; font-size: 4rem; font-weight: 800;
        text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        z-index: 1000; letter-spacing: 2px;
    }}
    .stHorizontalBlock {{
        position: fixed;
        bottom: 15%; left: 50%;
        transform: translateX(-50%);
        width: 60% !important;
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
# VISTA 2: CURRENT MONTH (DASHBOARD)
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
    def load_local_excel():
        try:
            df = pd.read_excel('Base bruta dic.xlsx')
            df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
            df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
            df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
            return df
        except: return pd.DataFrame()

    df = load_local_excel()
    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        font_main = dict(color="white", size=22)
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()

        with col_g1:
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(title={'text': "1. Primary Driver Composition", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
            fig2.update_layout(title={'text': "2. Average Score Per Primary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1: selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
        with c_f2:
            opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
            selector_cat = st.multiselect('Category:', opciones_cat, default=opciones_cat)

        df_filt = df.copy()
        if selector_driver != 'All': df_filt = df_filt[df_filt['Primary Driver'] == selector_driver]
        df_sec = df_filt[df_filt['Category'].isin(selector_cat)].copy()

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            conteo_cat = df_filt[df_filt['Category'] != 'N/A']['Category'].value_counts(normalize=True) * 100
            fig3 = go.Figure()
            color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
            for cat in ['Detractor', 'Passive', 'Promoter']:
                val = conteo_cat.get(cat, 0)
                fig3.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else ""))
            fig3.update_layout(title={'text':"3. Category Composition", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450)
            st.plotly_chart(fig3, use_container_width=True)

        with col_d2:
            if not df_sec.empty:
                data_vol = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00')
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450)
                st.plotly_chart(fig4, use_container_width=True)

        if not df_sec.empty:
            data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
            fig5 = px.bar(data_score, x='Label', y='Score', text=data_score['Score'].map('{:.2f}'.format))
            fig5.update_layout(title={'text': "5. Avg Score by Secondary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=500)
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #333;'><p style='color:#FFFF00; font-size:35px; font-weight:bold; text-align:center;'>CHOSEN COMMENTS</p>", unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        def render_card(col, key_id, default):
            with col:
                st.markdown(f'<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>', unsafe_allow_html=True)
                st.text_input("Secondary Driver:", value=default, key=f"t_{key_id}")
                st.text_input("Cliente:", key=f"cl_{key_id}")
                st.number_input("Score:", 0, 10, key=f"s_{key_id}")
                st.text_area("Comentario:", key=f"co_{key_id}", height=120)

        render_card(col_t1, "c1", "Secondary Driver 1:")
        render_card(col_t2, "c2", "Secondary Driver 2:")
        render_card(col_t3, "c3", "Secondary Driver 3:")

# ==========================================
# VISTA 3: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("""
        <style>
        .stApp { background-color: black; color: white; }
        .header-banner { background-color: #FFFF00; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 10px; }
        .header-title { color: black !important; font-family: 'Arial Black', sans-serif; font-size: 28px; margin: 0; text-align: center; flex-grow: 1; }
        .section-banner { background-color: #FFFF00; color: black !important; padding: 4px 10px; border-radius: 5px; text-align: center; margin-top: 15px; margin-bottom: 15px; font-weight: bold; }
        .logo-img { height: 70px; }
        div.stButton > button { background-color: #FFFF00 !important; color: black !important; font-weight: bold !important; }
        .stTextArea label { color: #FFFF00 !important; font-size: 22px !important; font-weight: bold !important; border: 2px solid #FFFF00; padding: 5px 10px; border-radius: 5px; display: inline-block; }
        .detractores-table { width: 100%; border-collapse: collapse; color: black; background-color: white; margin-bottom: 20px; }
        .detractores-table th { background-color: #1a3a4a; color: white; padding: 10px; border: 1px solid #ddd; }
        .detractores-table td { padding: 8px; border: 1px solid #ddd; text-align: center; color: black; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    def load_gsheet(url):
        try:
            csv_url = url.split('/edit')[0] + "/export?format=csv&gid=0"
            return pd.read_csv(StringIO(requests.get(csv_url).text), header=None)
        except: return pd.DataFrame()

    df_raw = load_gsheet("https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0")

    def render_block(df, row, title):
        meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        y25 = pd.to_numeric(df.iloc[row, 3:15], errors='coerce').tolist()
        bu = pd.to_numeric(df.iloc[row+1, 3:15], errors='coerce').tolist()
        y24 = pd.to_numeric(df.iloc[row+2, 3:15], errors='coerce').tolist()
        ytd25 = int(pd.to_numeric(df.iloc[row, 2], errors='coerce'))
        ytdbu = int(pd.to_numeric(df.iloc[row+1, 2], errors='coerce'))
        
        st.markdown(f'<div class="section-banner"><h2 style="color:black; margin:0; font-size:19px;">{title} | YTD {ytd25} vs BGT {ytdbu}</h2></div>', unsafe_allow_html=True)
        col_a, col_b = st.columns([3, 1.2])
        with col_a:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=meses, y=y25, mode='lines+markers+text', name="2025", line=dict(color='#FFFF00', width=4), text=y25, textposition="top center"))
            fig.add_trace(go.Scatter(x=meses, y=bu, mode='lines', name="Budget", line=dict(color='#FFD700', dash='dash')))
            fig.add_trace(go.Scatter(x=meses, y=y24, mode='lines+markers', name="2024", line=dict(color='#F4D03F')))
            fig.update_layout(title={'text': "Evolution", 'x': 0.5, 'xanchor': 'center'}, paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=450)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            figb = go.Figure(go.Bar(x=["2024", "BGT", "2025"], y=[df.iloc[row+2,2], ytdbu, ytd25], marker_color=['#F4D03F', '#FFD700', '#FFFF00']))
            figb.update_layout(title={'text': "YTD Comparison", 'x': 0.5, 'xanchor': 'center'}, paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=450)
            st.plotly_chart(figb, use_container_width=True)

    if not df_raw.empty:
        render_block(df_raw, 2, "NPS CD EL ALTO")
        render_block(df_raw, 7, "NPS EA")
        render_block(df_raw, 11, "NPS LP")
        
        st.markdown('<div class="section-banner">DETRACTORS</div>', unsafe_allow_html=True)
        st.write("Tabla de detractores y anillos YTD aquí...")

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App")
        with c2: st.text_area("Plan de Acción", height=150, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.")
        with c3: st.text_area("Key KPIs", height=150, value="• Canjes\n• Rechazo\n• On time")
