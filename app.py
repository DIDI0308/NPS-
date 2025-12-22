import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# --- ESTILO DARK MODE ---
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    .titulo-nps {
        text-align: center;
        color: #FFD700;
        font-family: 'Arial Black', Gadget, sans-serif;
        font-size: 42px;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA DE DATOS Y EXTRACCIÓN DEL MES ---
@st.cache_data
def load_data():
    # Asegúrate de que el archivo Excel esté en la misma carpeta
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    # Obtenemos el mes dinámico
    mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
    
    # Traducción rápida a español
    traducciones = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio', 
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    return df, traducciones.get(mes_nombre, mes_nombre)

df, mes_base = load_data()

# --- 2. ENCABEZADO CON LOGOS EN LAS ESQUINAS ---
# Creamos 3 columnas: [Izquierda (Logo2), Centro (Título), Derecha (Logo1)]
col_izq, col_centro, col_der = st.columns([1, 4, 1])

with col_izq:
    # Muestra logo2.png a la izquierda
    try:
        st.image("logo2.png", width=120)
    except:
        st.warning("No se encontró logo2.png")

with col_centro:
    # Título dinámico sin iconos
    st.markdown(f'<div class="titulo-nps">NPS 2025 - {mes_base}</div>', unsafe_allow_html=True)

with col_der:
    # Muestra logo.png a la derecha
    try:
        st.image("logo.png", width=120)
    except:
        st.warning("No se encontró logo.png")

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
    margin=dict(t=0, b=0, l=0, r=0)
)

st.plotly_chart(fig_pie, use_container_width=True)
