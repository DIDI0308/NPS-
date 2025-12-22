import streamlit as st
import base64

# Configuración de la página
st.set_page_config(page_title="NPS Performance", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_custom_style(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    style = f'''
    <style>
    /* Fondo de pantalla completa */
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* Título centrado vertical y horizontalmente */
    .main-title {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        width: 100%;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }}

    /* Contenedor de botones en la parte inferior */
    .button-footer {{
        position: fixed;
        bottom: 50px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 0 20px;
    }}

    /* Estilo para los botones amarillos */
    div.stButton > button {{
        background-color: #FFD700 !important; /* Amarillo */
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        width: 100% !important;
    }}
    
    div.stButton > button:hover {{
        background-color: #FFC400 !important; /* Amarillo más oscuro al pasar el mouse */
        color: black !important;
    }}
    </style>
    '''
    st.markdown(style, unsafe_allow_html=True)

# 1. Aplicar estilos y fondo
try:
    set_custom_style('logo3.png')
except FileNotFoundError:
    st.error("No se encontró 'logo3.png'. Verifica el nombre del archivo.")

# 2. Renderizar Título en el centro
st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)

# 3. Renderizar Botones en la parte inferior usando columnas de Streamlit
# Ponemos un espaciador para empujar el layout hacia abajo
st.markdown("<div style='height: 80vh;'></div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col2:
    if st.button("MONTHLY EVOLUTION"):
        st.write("Cargando Evolución...")

with col3:
    if st.button("CURRENT MONTH"):
        st.write("Cargando Mes Actual...")
