import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS REFINADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    
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
    .titulo-texto { text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }
    .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }
    .titulo-texto h2 { margin: 5px 0 0 0; font-size: 20px; text-transform: uppercase; }

    /* CONTENEDOR DE LA TARJETA */
    .plot-card {
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
        background-color: #FFFFFF; /* Fondo blanco para el cuerpo */
        border: 2px solid #FFFF00;
    }

    /* TÍTULO CON FONDO AMARILLO */
    .plot-header-yellow {
        background-color: #FFFF00 !important;
        color: #000000 !important;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        padding: 12px 0px;
        margin: 0px !important;
        width: 100%;
        display: block;
    }

    .plot-body-white {
        background-color: #FFFFFF;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Base bruta dic.xlsx')
        df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        df_filtrado = df[df['Primary Driver'] != 'N/A'].copy()
        mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
        traducciones = {'January': 'Enero', 'December': 'Diciembre'} # Simplificado para el ejemplo
        return df_filtrado, traducciones.get(mes_nombre, mes_nombre)
    except:
        return pd.DataFrame({'Primary Driver': ['Ejemplo'], 'Score': [10], 'Customer ID': [1]}), "Diciembre"

df, mes_base = load_data()

# --- HEADER / BANNER ---
b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
if b64_logo and b64_logo2:
    st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" class="logo-img"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" class="logo-img"></div>', unsafe_allow_html=True)

# --- CUERPO DE GRÁFICAS ---
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    # Inicio Tarjeta 1
    st.markdown('<div class="plot-card"><div class="plot-header-yellow">1. Primary Driver Composition</div><div class="plot-body-white">', unsafe_allow_html=True)
    
    data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
    fig_pie = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6,
                     color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D'])
    
    fig_pie.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color="black"),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        margin=dict(t=10, b=10, l=10, r=120),
        height=380
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with col2:
    # Inicio Tarjeta 2
    st.markdown('<div class="plot-card"><div class="plot-header-yellow">2. Average Score Per Primary Driver</div><div class="plot-body-white">', unsafe_allow_html=True)
    
    data_lineas = df.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
    data_lineas['Primary Driver Wrap'] = data_lineas['Primary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=12)))

    fig_lineas = px.line(data_lineas, x='Primary Driver Wrap', y='Score', markers=True)
    fig_lineas.update_traces(line_color='#FF8C00', marker=dict(size=10, color='#FF8C00'),
                             text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
    
    fig_lineas.update_layout(
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color="black"),
        yaxis=dict(gridcolor='#EEEEEE', title=None),
        xaxis=dict(title=None),
        margin=dict(t=40, b=60, l=10, r=10),
        height=380
    )
    st.plotly_chart(fig_lineas, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
