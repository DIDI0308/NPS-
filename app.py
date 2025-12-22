import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide", initial_sidebar_state="collapsed")

# Gestión de navegación entre pestañas
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS REFINADO ---
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

    /* TÍTULO ESTÉTICO ENORME (FONT 120) */
    .landing-title-container {{
        position: absolute;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        text-align: center;
        z-index: 5;
    }}
    .landing-title-line1 {{
        font-family: 'Arial Black', sans-serif;
        font-size: 110px; 
        font-weight: 900;
        color: #FFFFFF;
        text-shadow: 5px 5px 20px rgba(0,0,0,1);
        margin: 0;
        line-height: 1;
    }}
    .landing-title-line2 {{
        font-family: 'Arial Black', sans-serif;
        font-size: 130px; /* Tamaño máximo para impacto */
        font-weight: 900;
        color: #FFFFFF;
        text-shadow: 5px 5px 20px rgba(0,0,0,1);
        margin: 0;
        line-height: 1.1;
        letter-spacing: 10px;
    }}

    /* POSICIONAMIENTO FIJO DE BOTONES (NO SE MUEVEN) */
    .button-fixed-container {{
        position: absolute;
        bottom: 15%;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        gap: 80px; /* Espaciado entre los recuadros amarillos */
        z-index: 10;
    }}

    /* ESTILO ESTÉTICO DE BOTONES AMARILLOS SIN BORDE */
    div.stButton > button {{
        width: 320px !important;
        height: 80px !important;
        background-color: #FFFF00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.7);
        text-transform: uppercase;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: scale(1.05);
    }}

    /* ESTILOS DEL DASHBOARD INTERNO */
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
    # Imagen y Título Enorme
    st.markdown(f'''
        <div class="landing-wrapper">
            <div class="landing-title-container">
                <p class="landing-title-line1">NET PROMOTER SCORE</p>
                <p class="landing-title-line2">PERFORMANCE</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Contenedor de botones fijo sobre los recuadros
    st.markdown('<div style="height: 75vh;"></div>', unsafe_allow_html=True)
    col_l, col_btn1, col_gap, col_btn2, col_r = st.columns([1.5, 3, 0.4, 3, 1.5])
    
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
    st.markdown("<div style='padding: 20px;'>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()
    st.title("📈 MONTHLY EVOLUTION")
    st.info("Sección en desarrollo.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# VISTA: CURRENT MONTH (ANÁLISIS)
# ==========================================
elif st.session_state.page == 'current':
    st.markdown("<div style='padding: 20px;'>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        # Gráfica 1 y 2
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

        # Gráfica 3, 4, 5 y Comentarios (Resto del Dashboard...)
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        # [Insertar resto del código de filtros y gráficos aquí...]
        st.markdown('<p style="color:#FFFF00; font-size:35px; font-weight:bold; text-align:center;">CHOSEN COMMENTS </p>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        def render_dynamic_card(col, key_id, title):
            with col:
                st.markdown(f'''<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>''', unsafe_allow_html=True)
                st.text_input("Secondary Driver:", value=title, key=f"title_{key_id}")
                st.text_input("Cliente:", key=f"client_{key_id}")
                st.number_input("Score:", min_value=0, max_value=10, step=1, key=f"score_{key_id}")
                st.text_area("Comentario:", key=f"comment_{key_id}", height=120)
                st.text_input("Camión / Unidad:", key=f"truck_{key_id}")
        render_dynamic_card(col_t1, "c1", "Secondary Driver 1:")
        render_dynamic_card(col_t2, "c2", "Secondary Driver 2:")
        render_dynamic_card(col_t3, "c3", "Secondary Driver 3:")
    st.markdown("</div>", unsafe_allow_html=True)
