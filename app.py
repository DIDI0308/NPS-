import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Banner Principal */
    .banner-amarillo {
        background-color: #FFFF00; padding: 15px; display: flex;
        justify-content: space-between; align-items: center;
        border-radius: 5px; margin-bottom: 25px;
    }
    .titulo-texto { text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }
    .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; }

    /* Estilo Tarjetas de Comentarios */
    .card-container {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        color: #000000; /* Texto negro dentro de la tarjeta blanca */
    }
    .emoji-style {
        font-size: 60px;
        text-align: center;
        margin-bottom: 5px;
    }
    /* Estilo para los inputs dentro de las tarjetas */
    div[data-baseweb="input"] { background-color: #f9f9f9 !important; }
    label { color: #333333 !important; font-weight: bold !important; }
    
    /* Forzar fondo naranja en el primer input de la tarjeta (Driver) */
    .driver-header input {
        background-color: #FF8C00 !important;
        color: white !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Base bruta dic.xlsx')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
        mes = df['Survey Completed Date'].dt.month_name().iloc[0] if 'Survey Completed Date' in df.columns else "Mes"
        return df, mes
    except:
        return pd.DataFrame(), "Diciembre"

df, mes_base = load_data()

# --- HEADER ---
b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
if b64_logo and b64_logo2:
    st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

# --- (SECCIONES ANTERIORES DE GRÁFICAS AQUÍ...) ---
# (Para brevedad, omito el código de las gráficas 1-5 que ya tenemos listo)

# ==========================================
# SECCIÓN: COMMENTS CHOSEN (TARJETAS EDITABLES)
# ==========================================
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
st.markdown('<p style="color:white; font-size:26px; font-weight:bold; text-align:center;">COMMENTS CHOSEN</p>', unsafe_allow_html=True)

col_t1, col_t2, col_t3 = st.columns(3)

def renderizar_tarjeta(columna, id_tarjeta, default_driver):
    with columna:
        st.markdown(f'<div class="card-container">', unsafe_allow_html=True)
        st.markdown('<div class="emoji-style">☹</div>', unsafe_allow_html=True)
        
        # Inputs Editables
        st.text_input("Driver:", value=default_driver, key=f"driver_{id_tarjeta}", label_visibility="collapsed")
        
        c1, c2 = st.columns([2, 1])
        with c1: st.text_input("Cliente:", key=f"cliente_{id_tarjeta}")
        with c2: st.number_input("Score:", min_value=0, max_value=10, key=f"score_{id_tarjeta}")
        
        st.text_area("Comentario:", height=100, key=f"com_{id_tarjeta}")
        st.text_input("Camión:", key=f"camion_{id_tarjeta}")
        
        st.markdown('</div>', unsafe_allow_html=True)

renderizar_tarjeta(col_t1, 1, "Secondary Driver 1:")
renderizar_tarjeta(col_t2, 2, "Secondary Driver 2:")
renderizar_tarjeta(col_t3, 3, "Secondary Driver 3:")
