import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# Función para convertir imagen local a base64 (necesario para meter logos en HTML)
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ESTILO DARK MODE Y BANNER AMARILLO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    /* Contenedor del Banner Amarillo */
    .banner-amarillo {
        background-color: #FFFF00;
        padding: 10px;
        border-radius: 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 2px solid #FFFF00;
    }
    .logo-img {
        max-height: 100px;
    }
    .titulo-texto {
        text-align: center;
        flex-grow: 1;
        color: #000000; /* Texto negro sobre fondo amarillo */
        font-family: 'Arial Black', sans-serif;
    }
    .titulo-texto h1 {
        margin: 0;
        font-size: 60px;
        font-weight: 900;
    }
    .titulo-texto h2 {
        margin: 0;
        font-size: 25px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
    traducciones = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio', 
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    return df, traducciones.get(mes_nombre, mes_nombre)

df, mes_base = load_data()

# --- 2. GENERACIÓN DEL BANNER CON LOGOS ---
try:
    # Convertimos los logos a base64 para que el navegador los lea dentro del marco
    img_izq = f"data:image/png;base64,{get_base64('logo2.png')}"
    img_der = f"data:image/png;base64,{get_base64('logo.png')}"
    
    st.markdown(f"""
        <div class="banner-amarillo">
            <img src="{img_izq}" class="logo-img">
            <div class="titulo-texto">
                <h1>NPS 2025</h1>
                <h2>{mes_base}</h2>
            </div>
            <img src="{img_der}" class="logo-img">
        </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    # Si no encuentra los archivos, muestra un título simple para no romper la app
    st.warning("⚠️ Sube 'logo.png' y 'logo2.png' a la carpeta para ver el banner correctamente.")
    st.markdown(f"<h1 style='text-align:center; background-color:yellow; color:black;'>NPS 2025 - {mes_base}</h1>", unsafe_allow_html=True)

# --- 3. PRIMERA GRÁFICA (ANILLO) ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("1. Primary Driver Composition")

data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
fig_pie = px.pie(
    data_anillo, 
    values='Customer ID', 
    names='Primary Driver',
    hole=0.6,
    color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D']
)

fig_pie.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    legend_font_color="white",
    margin=dict(t=20, b=20, l=20, r=20)
)

st.plotly_chart(fig_pie, use_container_width=True)
