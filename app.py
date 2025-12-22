import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# --- ESTILO CSS ---
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
    .plot-title-solo-texto { color: #FFFFFF; text-align: left; font-weight: bold; font-size: 22px; margin-bottom: 5px; }
    
    /* Estilo para los selectores (Filtros) */
    .stSelectbox label, .stMultiSelect label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Base bruta dic.xlsx')
        df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
        df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        
        mes_nombre = df['Survey Completed Date'].dt.month_name().iloc[0]
        traducciones = {'January': 'Enero', 'December': 'Diciembre'} # Agregar más según mes
        return df, traducciones.get(mes_nombre, mes_nombre)
    except:
        # Data dummy para desarrollo
        data = {
            'Primary Driver': ['Logística', 'Producto', 'Logística'],
            'Secondary Driver': ['Tiempo Entrega', 'Calidad', 'Costo'],
            'Category': ['Promoter', 'Detractor', 'Passive'],
            'Score': [10, 5, 8],
            'Customer ID': [1, 2, 3]
        }
        return pd.DataFrame(data), "Diciembre"

df, mes_base = load_data()

# --- HEADER / BANNER ---
b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
if b64_logo and b64_logo2:
    st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" class="logo-img"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" class="logo-img"></div>', unsafe_allow_html=True)

# --- 1. GRÁFICAS GLOBALES (SIN FILTRO) ---
df_global = df[df['Primary Driver'] != 'N/A'].copy()
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown('<p class="plot-title-solo-texto">1. Primary Driver Composition</p>', unsafe_allow_html=True)
    data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
    fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6,
                  color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=350,
                       legend=dict(font=dict(color="white"), orientation="v", yanchor="middle", y=0.5, x=1.1))
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.markdown('<p class="plot-title-solo-texto">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
    data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
    fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
    fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'),
                       text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"),
                       yaxis=dict(gridcolor='#333333', title=None), height=350)
    st.plotly_chart(fig2, use_container_width=True)

# --- 2. PANEL INTERACTIVO (CON FILTROS) ---
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
st.markdown('<p class="plot-title-solo-texto">3. Panel Dinámico por Driver y Categoría</p>', unsafe_allow_html=True)

# Columnas para los filtros
c_f1, c_f2 = st.columns(2)
with c_f1:
    opciones_driver = ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A'])
    selector_driver = st.selectbox('Selecciona Primary Driver:', opciones_driver)

with c_f2:
    opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
    selector_cat = st.multiselect('Filtrar por Categoría:', opciones_cat, default=opciones_cat)

# --- LÓGICA DE FILTRADO DINÁMICO ---
df_filt = df.copy()
if selector_driver != 'All':
    df_filt = df_filt[df_filt['Primary Driver'] == selector_driver]

# Gráficas Dinámicas
col_d1, col_d2, col_d3 = st.columns([1, 2, 2])

with col_d1:
    # --- DINÁMICA A: CATEGORY COMPOSITION (Stacked Bar) ---
    df_visual_cat = df_filt[df_filt['Category'] != 'N/A']
    conteo_cat = df_visual_cat['Category'].value_counts(normalize=True) * 100
    
    orden = ['Detractor', 'Passive', 'Promoter']
    color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
    
    fig_stack = go.Figure()
    for cat in orden:
        val = conteo_cat.get(cat, 0)
        fig_stack.add_trace(go.Bar(
            name=cat, x=['Composition %'], y=[val],
            marker_color=color_map[cat],
            text=f"{val:.1f}%" if val > 0 else "",
            textposition='auto',
            textfont=dict(color='black', shadow="none")
        ))

    fig_stack.update_layout(
        barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"), height=450, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        yaxis=dict(range=[0, 100], visible=False)
    )
    st.markdown("<p style='text-align:center;'>Category Composition</p>", unsafe_allow_html=True)
    st.plotly_chart(fig_stack, use_container_width=True)

# Aquí puedes continuar con col_d2 y col_d3 para volumen y score por Secondary Driver
