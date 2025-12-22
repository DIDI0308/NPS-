import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página (esto siempre debe ir primero)
st.set_page_config(page_title="NPS Dashboard - Paso 1", layout="wide")

# Estilo para fondo negro (opcional, como lo pediste anteriormente)
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# 1. CARGA Y LIMPIEZA DE DATOS
@st.cache_data
def load_data():
    # Asegúrate de que el archivo Excel esté en la misma carpeta que este script
    df = pd.read_excel('Base bruta dic.xlsx')
    
    # Limpieza idéntica a tu código original
    df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
    df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
    df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    return df

# Ejecutar carga
df = load_data()

# TÍTULO DEL DASHBOARD
st.title("📊 NPS Dashboard 2025")

# --- GRÁFICA 1: PRIMARY DRIVER COMPOSITION ---
st.subheader("1. Primary Driver Composition")

# Preparación de datos para Plotly
data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
data_anillo.columns = ['Primary Driver', 'Total Customers']

# Definición de colores amarillos (consistente con tu paleta)
colores_amarillos = ['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D', '#F4D03F', '#F9E79F']

# Crear la gráfica con Plotly
fig_pie = px.pie(
    data_anillo, 
    values='Total Customers', 
    names='Primary Driver',
    hole=0.6, # Esto crea el efecto de "anillo"
    color_discrete_sequence=colores_amarillos
)

# Ajustes de diseño para que se vea bien en fondo negro
fig_pie.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    legend_font_color="white",
    title_font_color="white"
)

# Mostrar en Streamlit
st.plotly_chart(fig_pie, use_container_width=True)
