import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# Función para inyectar los logos en el banner HTML (Base64)
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

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
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .logo-img {
        max-height: 90px;
    }
    .titulo-texto {
        text-align: center;
        flex-grow: 1;
        color: #000000; 
        font-family: 'Arial Black', sans-serif;
    }
    .titulo-texto h1 {
        margin: 0;
        font-size: 55px;
        font-weight: 900;
        line-height: 1;
    }
    .titulo-texto h2 {
        margin: 5px 0 0 0;
        font-size: 22px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    # El archivo debe estar en la misma carpeta en GitHub
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
    
    # Obtener mes de la base
    mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
    traducciones = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio', 
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    return df, traducciones.get(mes_nombre, mes_nombre)

df, mes_base = load_data()

# --- 2. ENCABEZADO (BANNER AMARILLO) ---
b64_logo2 = get_base64('logo2.png')
b64_logo = get_base64('logo.png')

if b64_logo and b64_logo2:
    st.markdown(f"""
        <div class="banner-amarillo">
            <img src="data:image/png;base64,{b64_logo2}" class="logo-img">
            <div class="titulo-texto">
                <h1>NPS 2025</h1>
                <h2>{mes_base}</h2>
            </div>
            <img src="data:image/png;base64,{b64_logo}" class="logo-img">
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ Sube 'logo.png' y 'logo2.png' a GitHub para activar el banner.")
    st.markdown(f"<h1 style='text-align:center; background-color:yellow; color:black; padding:20px;'>NPS 2025 - {mes_base}</h1>", unsafe_allow_html=True)

# --- 3. SECCIÓN DE GRÁFICAS GLOBALES (FILA 1) ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Resumen Global de Satisfacción")

# Layout de dos columnas
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 1. Primary Driver Composition")
    data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
    
    fig_pie = px.pie(
        data_anillo, 
        values='Customer ID', 
        names='Primary Driver',
        hole=0.6,
        color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D'],
        template="plotly_dark"
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        legend_font_color="white",
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("#### 2. Average Score Per Primary Driver")
    data_lineas = df.groupby('Primary Driver')['Score'].mean().sort_values(ascending=False).reset_index()
    
    fig_lineas = px.line(
        data_lineas, 
        x='Primary Driver', 
        y='Score', 
        text=data_lineas['Score'].apply(lambda x: f'{x:.2f}'),
        markers=True,
        template="plotly_dark"
    )
    
    fig_lineas.update_traces(
        line_color='#FFD700', 
        line_width=3,
        marker=dict(size=12, color='#FFD700'),
        textposition="top center",
        textfont=dict(color="white", size=13)
    )
    
    fig_lineas.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[6, 10], gridcolor='#333333', title="Avg Score"),
        xaxis=dict(tickangle=45, title="Primary Driver"),
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_lineas, use_container_width=True)
    
