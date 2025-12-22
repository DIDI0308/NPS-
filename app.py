import streamlit as st
import base64

# Configuración de la página
st.set_page_config(page_title="NPS Performance", layout="wide")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_full_screen_ui(bin_file):
    bin_str = get_base64(bin_file)
    style = f'''
    <style>
    /* 1. Fondo fijo sin scroll */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        overflow: hidden; 
        height: 100vh;
    }}

    /* 2. Ocultar elementos de Streamlit */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .block-container {{padding: 0 !important;}}

    /* 3. Contenedor Maestro Centrado */
    .main-container {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        width: 80%;
        z-index: 1000;
    }}

    .main-title {{
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 40px; /* Espacio entre título y botones */
        text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    /* 4. Estilo de los botones Amarillos */
    div.stButton > button {{
        background-color: #FFFF00 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: none !important;
        padding: 12px 25px !important;
        border-radius: 8px !important;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
        width: 250px !important; /* Ancho fijo para simetría */
    }}
    
    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: translateY(-2px);
    }}
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

# Aplicar diseño
try:
    set_full_screen_ui('logo3.png')
except FileNotFoundError:
    st.error("Archivo 'logo3.png' no encontrado.")

# --- ESTRUCTURA DE LA PÁGINA ---

# Abrimos el contenedor principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Título
st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)

# Botones debajo del título
col_left, col1, col2, col_right = st.columns([1, 2, 2, 1])

with col1:
    if st.button("MONTHLY EVOLUTION"):
        st.toast("Cargando Evolución Mensual...")

with col2:
    if st.button("CURRENT MONTH"):
        st.toast("Cargando Mes Actual...")

# Cerramos el contenedor
st.markdown('</div>', unsafe_allow_html=True)
