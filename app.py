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
    except:
        return None
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
        height: 100vh;
        width: 100vw;
    }}
    header {{visibility: hidden;}}
    .main-title {{
        position: fixed;
        top: 40%; left: 50%;
        transform: translate(-50%, -50%);
        color: white; font-size: 3.5rem; font-weight: 800;
        text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
    }}
    div.stButton > button {{
        background-color: #FFFF00 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }}
    </style>
    '''
    st.markdown(style_home, unsafe_allow_html=True)
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.page = "monthly"
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with col3:
        if st.button("EA / LP", use_container_width=True):
            st.session_state.page = "ea_lp"
            st.rerun()

# ==========================================
# VISTA 2: DASHBOARD (CURRENT MONTH)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown("<style>.stApp { background-color: #000000; color: white; }</style>", unsafe_allow_html=True)
    
    if st.button("⬅ VOLVER"):
        st.session_state.page = "home"
        st.rerun()

    @st.cache_data(ttl=600)
    def load_data(url):
        try:
            csv_url = url.split('/edit')[0] + "/export?format=csv"
            res = requests.get(csv_url)
            return pd.read_csv(StringIO(res.text))
        except: return pd.DataFrame()

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit?usp=sharing"
    df = load_data(SHEET_URL)

    if not df.empty:
        st.title("Current Month Performance")
        # Aquí irían tus gráficas de la Vista 2 (Anillo, Líneas, etc.)
        st.write("Datos cargados correctamente.")
    else:
        st.warning("No se pudieron cargar los datos.")

# ==========================================
# VISTA 3: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER"):
        st.session_state.page = "home"
        st.rerun()
    st.title("Monthly Evolution")
    # Lógica de Vista 3...

# ==========================================
# VISTA 4: EA / LP (CORREGIDA)
# ==========================================
elif st.session_state.page == "ea_lp":
    def get_ea_lp_data():
        try:
            u = "https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit?usp=sharing".split('/edit')[0]
            csv_url = f"{u}/export?format=csv&nocache={pd.Timestamp.now().timestamp()}"
            res = requests.get(csv_url)
            return pd.read_csv(StringIO(res.text))
        except:
            return pd.DataFrame()

    st.markdown("""
        <style>
        .stApp { background-color: #000000 !important; }
        .banner-ea-lp { background-color: #FFFF00; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
        h2 { color: black !important; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown('<div class="banner-ea-lp"><h2>PERFORMANCE EA / LP</h2></div>', unsafe_allow_html=True)

    df_raw = get_ea_lp_data()

    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df_raw['Primary Driver'] = df_raw['Primary Driver'].astype(str).str.upper()
        df_delivery = df_raw[df_raw['Primary Driver'] == 'DELIVERY'].copy()

        def clean_reg(x):
            x = str(x).upper()
            if 'ALTO' in x or 'EA' in x: return 'EA'
            if 'PAZ' in x or 'LP' in x: return 'LP'
            return 'OTRO'
        
        df_delivery['REG_GROUP'] = df_delivery['Sales Region'].apply(clean_reg)
        df_final = df_delivery[df_delivery['REG_GROUP'].isin(['EA', 'LP'])].copy()

        if not df_final.empty:
            col_izq, col_der = st.columns([1.5, 2.5])
            
            with col_izq:
                st.markdown('<p style="color:#FFFF00; font-size:18px; font-weight:bold;">CLIENT DISTRIBUTION</p>', unsafe_allow_html=True)
                df_plot = df_final.groupby(['Category', 'REG_GROUP']).size().reset_index(name='Counts')
                fig = px.bar(df_plot, x="Category", y="Counts", color="REG_GROUP", barmode="stack",
                             color_discrete_map={'EA': '#FFFF00', 'LP': '#DAA520'})
                fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_der:
                st.markdown('<p style="color:#FFFF00; font-size:18px; font-weight:bold;">SECONDARY DRIVER BY REGION</p>', unsafe_allow_html=True)
                df_horiz_data = df_final.groupby(['Secondary Driver', 'REG_GROUP']).size().reset_index(name='Cuenta')
                
                # LA LÍNEA QUE DABA ERROR AHORA ESTÁ BIEN INDENTADA:
                fig_horiz = px.bar(
                    df_horiz_data, 
                    y="Secondary Driver", 
                    x="Cuenta", 
                    color="REG_GROUP",
                    orientation='h', 
                    text="Cuenta",
                    color_discrete_map={'EA': '#FFFF00', 'LP': '#CC9900'},
                    template="plotly_dark"
                )
                fig_horiz.update_layout(paper_bgcolor='black', plot_bgcolor='black', height=450)
                st.plotly_chart(fig_horiz, use_container_width=True)
        else:
            st.warning("No hay datos de Delivery para EA o LP.")
    else:
        st.error("No se pudo conectar con la base de datos.")
