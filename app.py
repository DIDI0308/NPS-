import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Performance 2025", layout="wide", initial_sidebar_state="collapsed")

# Gestión de navegación entre pestañas
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS REFINADO (MÁXIMO IMPACTO VISUAL) ---
b64_bg = get_base64('logo3.png')

st.markdown(f"""
    <style>
    /* ELIMINAR MÁRGENES DE STREAMLIT */
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) {{
        padding: 0px;
    }}
    .stApp {{ background-color: #000000; color: #FFFFFF; }}
    
    /* LANDING FULL SCREEN */
    .landing-wrapper {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        {" background-image: url('data:image/png;base64," + b64_bg + "');" if b64_bg else ""}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    
    .landing-title-line2 {{
        font-family: 'Arial Black', sans-serif;
        font-size: 190px; 
        font-weight: 900;
        margin: 0;
        line-height: 1.0;
        letter-spacing: 25px;
        text-transform: uppercase;
        /* Color Amarillo Vibrante con degradado */
        background: linear-gradient(180deg, #FFFF00 0%, #FFCC00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0px 20px 30px rgba(0,0,0,1));
    }}

    /* BOTONES TOTALMENTE FIJOS (SISTEMA DE ANCLAJE) */
    .stButton {{
        position: fixed;
        bottom: 12vh;
        z-index: 100;
    }}
    
    /* Anclaje exacto para Botón Izquierdo */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stButton {{
        left: 20vw;
    }}
    
    /* Anclaje exacto para Botón Derecho */
    div[data-testid="stVerticalBlock"] > div:nth-child(4) .stButton {{
        right: 20vw;
    }}

    /* ESTILO BOTONES (AMARILLO PURO, SIN BORDE) */
    div.stButton > button {{
        width: 350px !important;
        height: 90px !important;
        background-color: #FFFF00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.8);
        text-transform: uppercase;
        transition: all 0.2s ease-in-out;
    }}

    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: scale(1.05) translateY(-5px);
        box-shadow: 0px 20px 45px rgba(255, 255, 0, 0.4);
    }}

    /* ESTILOS DASHBOARD INTERNO */
    .banner-amarillo {{
        background-color: #FFFF00; padding: 15px; display: flex;
        justify-content: space-between; align-items: center;
        border-radius: 5px; margin: 20px;
    }}
    .titulo-texto {{ text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }}
    .titulo-texto h1 {{ margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }}

    .card-transparent {{
        background-color: rgba(255, 255, 255, 0.05);
        border: none; border-radius: 15px; padding: 15px; margin-bottom: 20px;
    }}
    .emoji-solid-yellow {{
        font-size: 110px; text-align: center; color: #FFFF00;
        text-shadow: 0 0 0 #FFFF00; line-height: 1; margin-bottom: 15px; display: block;
    }}
    label {{ color: #FFFF00 !important; font-weight: bold !important; }}
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{
        background-color: #1A1A1A !important; color: white !important; border: 1px solid #333 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Base bruta dic.xlsx')
        df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
        df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
        traducciones = {'January': 'Enero', 'December': 'Diciembre'}
        return df, traducciones.get(mes_nombre, mes_nombre)
    except:
        return pd.DataFrame(), "Mes"

df, mes_base = load_data()

# ==========================================
# VISTA: LANDING PAGE
# ==========================================
if st.session_state.page == 'landing':
    st.markdown(f'''
        <div class="landing-wrapper">
            <div class="landing-title-container">
                <p class="landing-title-line1">NET PROMOTER SCORE</p>
                <p class="landing-title-line2">PERFORMANCE</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Grid de botones anclados por CSS
    col_l, col_btn1, col_gap, col_btn2, col_r = st.columns([1, 4, 1, 4, 1])
    
    with col_btn1:
        if st.button("MONTHLY EVOLUTION", key="btn_evo"):
            st.session_state.page = 'evolution'
            st.rerun()
    
    with col_btn2:
        if st.button("CURRENT MONTH", key="btn_curr"):
            st.session_state.page = 'current'
            st.rerun()

# ==========================================
# VISTA: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == 'evolution':
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()
    st.title("📈 MONTHLY EVOLUTION")
    st.info("Sección en desarrollo.")

# ==========================================
# VISTA: CURRENT MONTH (ANÁLISIS COMPLETO)
# ==========================================
elif st.session_state.page == 'current':
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()
        with col_g1:
            st.markdown('<p style="font-size:22px; font-weight:bold;">1. Primary Driver Composition</p>', unsafe_allow_html=True)
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400, legend=dict(font=dict(color="white")))
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            st.markdown('<p style="font-size:22px; font-weight:bold;">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), yaxis=dict(gridcolor='#333333', title=None))
            st.plotly_chart(fig2, use_container_width=True)
