import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# --- ESTILO CSS ---
b64_bg = get_base64('logo3.png')

st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) {{
    padding: 0px;
}}
.stApp {{ background-color: #000000; color: #FFFFFF; }}

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

.landing-title {{
    position: fixed;
    top: 38%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    text-align: center;
    font-family: 'Arial Black', sans-serif;
    font-size: 65px;
    font-weight: 900;
    color: #FFFFFF;
    text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
    letter-spacing: 2px;
    line-height: 1.1;
    z-index: 5;
}}

.landing-buttons {{
    position: fixed;
    bottom: 8%;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 50px;
    z-index: 10;
}}

div.stButton > button {{
    width: 320px !important;
    height: 80px !important;
    background-color: #FFFF00 !important;
    color: #000000 !important;
    font-weight: 900 !important;
    font-size: 20px !important;
    border-radius: 15px !important;
    border: 4px solid #000000 !important;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
    text-transform: uppercase;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}

div.stButton > button:hover {{
    background-color: #FFEA00 !important;
    transform: scale(1.1);
    box-shadow: 0px 12px 30px rgba(255, 255, 0, 0.4);
}}

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
    line-height: 1; margin-bottom: 15px; display: block;
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
# LANDING
# ==========================================
if st.session_state.page == 'landing':
    st.markdown("""
        <div class="landing-wrapper"></div>
        <div class="landing-title">
            NET PROMOTER SCORE<br>PERFORMANCE
        </div>
        <div class="landing-buttons">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION"):
            st.session_state.page = 'evolution'
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH"):
            st.session_state.page = 'current'
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == 'evolution':
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()
    st.title("📈 MONTHLY EVOLUTION")
    st.info("Esta sección se encuentra en desarrollo.")

# ==========================================
# CURRENT MONTH
# ==========================================
elif st.session_state.page == 'current':
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'''
        <div class="banner-amarillo">
            <img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;">
            <div class="titulo-texto">
                <h1>NPS 2025</h1>
                <h2>{mes_base}</h2>
            </div>
            <img src="data:image/png;base64,{b64_logo}" style="max-height:80px;">
        </div>
        ''', unsafe_allow_html=True)
