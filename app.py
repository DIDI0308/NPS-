import streamlit as st
import base64

# Configuración de la página
st.set_page_config(page_title="NPS Performance", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Estilo para que el título sea legible sobre el fondo */
    h1 {{
        color: white;
        text-shadow: 2px 2px 4px #000000;
        padding-top: 50px;
    }}

    /* Contenedor inferior para los botones */
    .button-container {{
        position: fixed;
        bottom: 10%;
        left: 0;
        right: 0;
        padding: 0 10%;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# 1. Aplicar el fondo (asegúrate de que logo3.png esté en la misma carpeta)
try:
    set_png_as_page_bg('logo3.png')
except FileNotFoundError:
    st.error("No se encontró el archivo logo3.png. Asegúrate de que esté en la misma carpeta que este script.")

# 2. Título principal centrado
st.markdown("<h1 style='text-align: center;'>NET PROMOTER SCORE PERFORMANCE</h1>", unsafe_allow_html=True)

# 3. Espaciador para empujar los botones hacia abajo
st.markdown("<div style='height: 60vh;'></div>", unsafe_allow_html=True)

# 4. Botones en la parte inferior
col1, col2 = st.columns(2)

with col1:
    if st.button("MONTHLY EVOLUTION", use_container_width=True):
        st.write("Has seleccionado Evolución Mensual")

with col2:
    if st.button("CURRENT MONTH", use_container_width=True):
        st.write("Has seleccionado Mes Actual")
