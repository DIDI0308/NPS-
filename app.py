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
    /* Bloquear scroll y configurar fondo */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        overflow: hidden; 
        height: 100vh;
        width: 100vw;
    }}

    header {{visibility: hidden;}}
    .block-container {{
        padding: 0 !important;
    }}

    /* Título y Mensajes en el centro */
    .main-title {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        z-index: 1000;
        letter-spacing: 2px;
    }}

    /* Contenedor de botones en la PARTE INFERIOR */
    .stHorizontalBlock {{
        position: fixed;
        bottom: 10%; 
        left: 50%;
        transform: translateX(-50%);
        width: 50% !important;
        z-index: 1001;
    }}

    /* Estilo de botones Amarillos */
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
    
    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: scale(1.05);
    }}
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

# 1. Aplicar diseño e imagen
try:
    set_full_screen_ui('logo3.png')
except FileNotFoundError:
    st.error("Error: 'logo3.png' no encontrado.")

# Inicializar el estado de la sesión para saber si se hizo clic
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

# 2. Lógica de visualización
if not st.session_state.clicked:
    # Mostrar Título
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)

    # Mostrar Botones en la parte inferior
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.clicked = True
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.clicked = True
            st.rerun()
else:
    # Mensaje de "Aún trabajando" en el centro
    st.markdown('<div class="main-title">AÚN TRABAJANDO...</div>', unsafe_allow_html=True)
    
    # Botón opcional para volver atrás
    cols = st.columns([2,1,2])
    with cols[1]:
        if st.button("VOLVER"):
            st.session_state.clicked = False
            st.rerun()
