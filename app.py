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
        overflow: hidden; /* Elimina el scroll */
        height: 100vh;
        width: 100vw;
    }}

    /* Eliminar headers y paddings sobrantes de Streamlit */
    header {{visibility: hidden;}}
    .block-container {{
        padding: 0 !important;
    }}

    /* Título en el centro exacto */
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

    /* Contenedor de botones en el centro inferior */
    .bottom-container {{
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 20px;
        z-index: 1001;
    }}

    /* Estilo de botones Amarillos */
    div.stButton > button {{
        background-color: #FFFF00 !important; /* Amarillo puro */
        color: black !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        transition: 0.3s;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }}
    
    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: scale(1.05);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
    }}
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

# 1. Aplicar diseño e imagen
try:
    set_full_screen_ui('logo3.png')
except FileNotFoundError:
    st.error("Error: 'logo3.png' no encontrado.")

# 2. Título (HTML para control total de posición)
st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)

# 3. Botones (Usamos columnas dentro de un contenedor fijo simulado)
# Nota: Streamlit necesita que los widgets estén en el flujo, pero el CSS los posicionará
col_spacer1, col1, col2, col_spacer2 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("MONTHLY EVOLUTION", use_container_width=True):
        st.toast("Cargando Evolución Mensual...")

with col2:
    if st.button("CURRENT MONTH", use_container_width=True):
        st.toast("Cargando Mes Actual...")
