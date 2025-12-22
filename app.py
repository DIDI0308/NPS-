import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import textwrap

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

# --- ESTILO DARK MODE CON TARJETAS BLANCAS ---
st.markdown("""
    <style>
    /* Fondo general de la web en negro */
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
        margin-bottom: 25px;
    }
    .logo-img { max-height: 80px; }
    .titulo-texto {
        text-align: center;
        flex-grow: 1;
        color: #000000; 
        font-family: 'Arial Black', sans-serif;
    }
    .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }
    .titulo-texto h2 { margin: 5px 0 0 0; font-size: 20px; text-transform: uppercase; }

    /* ESTILO DE LAS TARJETAS DE GRÁFICAS (FONDO BLANCO) */
    .plot-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .plot-title {
        color: #000000;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
    
    # Filtro: Excluir N/A
    df_filtrado = df[df['Primary Driver'] != 'N/A'].copy()
    
    mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
    traducciones = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio', 
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    return df_filtrado, traducciones.get(mes_nombre, mes_nombre)

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
    st.markdown(f"<h1 style='text-align:center; background-color:yellow; color:black; padding:20px; border-radius:5px;'>NPS 2025 - {mes_base}</h1>", unsafe_allow_html=True)

# --- 3. SECCIÓN DE GRÁFICAS (FILA 1) ---
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Contenedor Blanco
    st.markdown('<div class="plot-card"><p class="plot-title">1. Primary Driver Composition</p>', unsafe_allow_html=True)
    data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
    
    fig_pie = px.pie(
        data_anillo, 
        values='Customer ID', 
        names='Primary Driver',
        hole=0.6,
        color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D'],
        template="plotly_white" # Cambiado a template blanco
    )
    fig_pie.update_layout(
        height=380,
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color="black"), # Texto de leyenda en negro
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        margin=dict(t=10, b=10, l=10, r=120) 
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Contenedor Blanco
    st.markdown('<div class="plot-card"><p class="plot-title">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
    data_lineas = df.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
    data_lineas['Primary Driver Wrap'] = data_lineas['Primary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=12)))

    fig_lineas = px.line(
        data_lineas, 
        x='Primary Driver Wrap', 
        y='Score', 
        markers=True,
        template="plotly_white" # Cambiado a template blanco
    )
    
    fig_lineas.update_traces(
        line_color='#FF8C00', # Naranja para que resalte en el fondo blanco
        line_width=3,
        marker=dict(size=10, color='#FF8C00'),
        text=data_lineas['Score'].map('{:.2f}'.format),
        textposition="top center",
        mode='lines+markers+text',
        textfont=dict(color="black") # Números de score en negro
    )
    
    fig_lineas.update_layout(
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="black"), # Ejes en negro
        yaxis=dict(range=[min(data_lineas['Score']) - 0.5, 10.5], gridcolor='#EEEEEE', title=None),
        xaxis=dict(title=None, tickangle=0),
        margin=dict(t=20, b=60, l=10, r=10)
    )
    st.plotly_chart(fig_lineas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
