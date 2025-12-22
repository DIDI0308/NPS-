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
        font-size: 50px;
        margin-bottom: 0px;
    }
    .sub-info {
        text-align: center;
        color: #FFFFFF;
        font-size: 20px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA Y EXTRACCIÓN DEL MES ---
@st.cache_data
def load_data_and_get_month():
    # Cargamos el archivo
    df = pd.read_excel('Base bruta dic.xlsx')
    
    # Limpieza y conversión de fechas
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    
    # Extraemos el nombre del mes en español (o inglés según tu sistema)
    # Tomamos el mes de la primera fila disponible
    mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
    
    # Traducción manual rápida si es necesario (opcional)
    traducciones = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio', 
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    mes_final = traducciones.get(mes_nombre, mes_nombre)
    
    return df, mes_final

# Ejecutar carga
df, mes_base = load_data_and_get_month()

# --- 2. TÍTULO CON ICONOS ---
# Usamos HTML para combinar el texto, el mes dinámico y los iconos
st.markdown(f"""
    <div class="titulo-nps">
        📊 NPS 2025 - {mes_base} 📈
    </div>
    <div class="sub-info">
        Análisis Operativo de Satisfacción del Cliente
    </div>
    """, unsafe_allow_html=True)

# --- 3. PRIMERA GRÁFICA (ANILLO) ---
st.markdown("---")
st.subheader("1. Primary Driver Composition")

data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
data_anillo.columns = ['Primary Driver', 'Total Customers']
colores_amarillos = ['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D', '#F4D03F']

fig_pie = px.pie(
    data_anillo, 
    values='Total Customers', 
    names='Primary Driver',
    hole=0.6,
    color_discrete_sequence=colores_amarillos
)

fig_pie.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    legend_font_color="white"
)

st.plotly_chart(fig_pie, use_container_width=True)
