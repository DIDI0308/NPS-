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

# --- ESTILO CSS (DARK MODE) ---
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
        traducciones = {'January': 'Enero', 'December': 'Diciembre'}
        return df, traducciones.get(mes_nombre, mes_nombre)
    except:
        data = {
            'Primary Driver': ['Logística', 'Producto', 'Atención'],
            'Secondary Driver': ['Tiempo', 'Calidad', 'Cordialidad'],
            'Category': ['Promoter', 'Detractor', 'Passive'],
            'Score': [10, 5, 8], 'Customer ID': [1, 2, 3]
        }
        return pd.DataFrame(data), "Diciembre"

df, mes_base = load_data()

# --- HEADER ---
b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
if b64_logo and b64_logo2:
    st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" class="logo-img"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" class="logo-img"></div>', unsafe_allow_html=True)

# --- GRÁFICAS ESTÁTICAS ---
st.markdown("<br>", unsafe_allow_html=True)
df_global = df[df['Primary Driver'] != 'N/A'].copy()
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown('<p class="plot-title-solo-texto">1. Primary Driver Composition</p>', unsafe_allow_html=True)
    data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
    fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400, legend=dict(font=dict(color="white"), orientation="v", yanchor="middle", y=0.5, x=1.02))
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.markdown('<p class="plot-title-solo-texto">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
    data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
    fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
    fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text', textfont=dict(color="white"))
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), yaxis=dict(gridcolor='#333333', title=None), height=400)
    st.plotly_chart(fig2, use_container_width=True)

# --- PANEL INTERACTIVO ---
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
c_f1, c_f2 = st.columns(2)
with c_f1:
    selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
with c_f2:
    selector_cat = st.multiselect('Category:', sorted([cat for cat in df['Category'].unique() if cat != 'N/A']), default=sorted([cat for cat in df['Category'].unique() if cat != 'N/A']))

df_filt = df.copy()
if selector_driver != 'All': df_filt = df_filt[df_filt['Primary Driver'] == selector_driver]
df_filt = df_filt[df_filt['Category'].isin(selector_cat)]

col_d1, col_d2 = st.columns([1, 2])

with col_d1:
    # --- GRÁFICA 3: CATEGORY COMPOSITION ---
    df_visual_cat = df_filt[df_filt['Category'] != 'N/A']
    if not df_visual_cat.empty:
        conteo_cat = df_visual_cat['Category'].value_counts(normalize=True) * 100
        orden = ['Detractor', 'Passive', 'Promoter']
        color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
        fig_stack = go.Figure()
        for cat in orden:
            val = conteo_cat.get(cat, 0)
            fig_stack.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else "", textposition='auto', textfont=dict(color='black', size=14)))
        
        fig_stack.update_layout(
            title={'text': "3. Category Composition", 'y': 0.98, 'x': 0.5, 'xanchor': 'center', 'font': {'color': 'white', 'size': 20}},
            barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=500,
            showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(color="white", size=12)),
            yaxis=dict(range=[0, 105], visible=False), margin=dict(t=60, b=100)
        )
        st.plotly_chart(fig_stack, use_container_width=True)

with col_d2:
    # --- GRÁFICA 4: SECONDARY DRIVER (TÍTULO MÁS CERCA) ---
    if not df_filt.empty:
        data_sec = df_filt.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values('Score')
        fig_sec = px.bar(data_sec, x='Score', y='Secondary Driver', orientation='h', text_auto='.2f')
        fig_sec.update_traces(marker_color='#FFD700', textfont=dict(color='black'))
        fig_sec.update_layout(
            title={'text': f"4. Score por Secondary Driver: {selector_driver}", 'y': 0.98, 'x': 0.5, 'xanchor': 'center', 'font': {'color': 'white', 'size': 20}},
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"),
            xaxis=dict(gridcolor='#333333', title=None), yaxis=dict(title=None),
            height=500, margin=dict(t=60, b=50) # 't=60' pega el título a la gráfica
        )
        st.plotly_chart(fig_sec, use_container_width=True)
