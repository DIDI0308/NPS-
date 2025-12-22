import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide", initial_sidebar_state="collapsed")

# Gestión de navegación
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS PARA POSICIONAMIENTO FIJO ---
b64_bg = get_base64('logo3.png')

st.markdown(f"""
    <style>
    /* Reset de márgenes y eliminación de scroll en landing */
    [data-testid="stAppViewContainer"] {{
        background-color: #000000;
    }}
    .main .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}
    header {{display: none !important;}} 

    /* FONDO FULL SCREEN */
    .landing-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 1;
        {"background-image: url('data:image/png;base64," + b64_bg + "');" if b64_bg else ""}
        background-size: 100% 100%;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* ANCLAJE INMÓVIL PARA BOTONES LANDING */
    .stButton {{
        position: fixed;
        z-index: 1000;
    }}

    /* Botón Izquierdo (Monthly Evolution) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton {{
        bottom: 15vh;
        left: 21vw;
    }}

    /* Botón Derecho (Current Month) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) .stButton {{
        bottom: 15vh;
        right: 21vw;
    }}

    /* Botón VOLVER AL INICIO (Dashboard) */
    .back-btn-fixed .stButton {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 2000;
    }}

    /* ESTILO ESTÉTICO DE LOS BOTONES */
    div.stButton > button {{
        width: 330px !important;
        height: 85px !important;
        background-color: #FFFF00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.7);
        text-transform: uppercase;
        transition: 0.3s;
    }}

    div.stButton > button:hover {{
        transform: scale(1.05);
        background-color: #FFEA00 !important;
    }}

    /* ESTILOS DASHBOARD */
    .dashboard-container {{
        background-color: #000000;
        min-height: 100vh;
        padding: 40px 20px 20px 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Base bruta dic.xlsx')
        df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        for col in ['Primary Driver', 'Secondary Driver', 'Category']:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', 'N/A')
        mes = df['Survey Completed Date'].dt.month_name().iloc[0] if not df.empty else "Mes"
        return df, mes
    except:
        return pd.DataFrame(), "Diciembre"

df, mes_base = load_data()

# ==========================================
# VISTA: LANDING PAGE
# ==========================================
if st.session_state.page == 'landing':
    st.markdown('<div class="landing-bg"></div>', unsafe_allow_html=True)
    
    # Creamos las columnas necesarias para que el CSS identifique los botones
    st.markdown('<div style="height: 100vh;"></div>', unsafe_allow_html=True) 
    col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 4, 1])
    
    with col2:
        if st.button("MONTHLY EVOLUTION", key="btn_evo"):
            st.session_state.page = 'evolution'
            st.rerun()
            
    with col4:
        if st.button("CURRENT MONTH", key="btn_curr"):
            st.session_state.page = 'current'
            st.rerun()

# ==========================================
# VISTA: CURRENT MONTH (DASHBOARD)
# ==========================================
elif st.session_state.page == 'current':
    # Botón de volver con clase fija
    st.markdown('<div class="back-btn-fixed">', unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    st.markdown(f'''
        <div style="background-color:#FFFF00; padding:15px; display:flex; justify-content:space-between; align-items:center; border-radius:10px; margin-bottom:25px; margin-top:50px;">
            <img src="data:image/png;base64,{b64_logo2}" style="max-height:70px;">
            <div style="text-align:center; flex-grow:1; color:#000000; font-family:'Arial Black';">
                <h1 style="margin:0; font-size:45px;">NPS 2025</h1>
                <h2 style="margin:0; font-size:20px;">{mes_base}</h2>
            </div>
            <img src="data:image/png;base64,{b64_logo}" style="max-height:70px;">
        </div>
    ''', unsafe_allow_html=True)

    if not df.empty:
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()
        
        with col_g1:
            st.markdown('<p style="font-size:22px; font-weight:bold; color:white;">1. Primary Driver Composition</p>', unsafe_allow_html=True)
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_g2:
            st.markdown('<p style="font-size:22px; font-weight:bold; color:white;">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10))
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# VISTA: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == 'evolution':
    st.markdown('<div class="back-btn-fixed">', unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO", key="back_evo"):
        st.session_state.page = 'landing'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    st.title("📈 Monthly Evolution")
    st.info("Sección en desarrollo.")
    st.markdown('</div>', unsafe_allow_html=True)
