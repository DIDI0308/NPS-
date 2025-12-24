import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap
from io import StringIO
import requests
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# --- FUNCIONES DE UTILIDAD ---
def get_base64(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return None
    return None

# --- MANEJO DE ESTADO DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

# ==========================================
# VISTA 1: HOME
# ==========================================
if st.session_state.page == "home":
    bin_str = get_base64('logo3.png')
    style_home = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str if bin_str else ""}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        overflow: hidden; height: 100vh; width: 100vw;
    }}
    header {{visibility: hidden;}}
    .block-container {{padding: 0 !important;}}
    .main-title {{
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 4rem; font-weight: 800; text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8); z-index: 1000;
    }}
    .stHorizontalBlock {{
        position: fixed; bottom: 10%; left: 50%; transform: translateX(-50%); width: 50% !important; z-index: 1001;
    }}
    div.stButton > button {{
        background-color: #FFFF00 !important; color: black !important; font-weight: bold !important;
        font-size: 18px !important; border: none !important; padding: 15px 30px !important; border-radius: 10px !important;
    }}
    </style>
    '''
    st.markdown(style_home, unsafe_allow_html=True)
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.page = "monthly"; st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"; st.rerun()

# ==========================================
# VISTA 2: DASHBOARD (CURRENT MONTH)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; overflow: auto !important; }
        div[data-testid="stButton"] button { background-color: #FFFF00 !important; color: #000000 !important; font-weight: bold !important; }
        .banner-amarillo { background-color: #FFFF00; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 25px; }
        .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; color: black; text-align: center; width: 100%; }
        .card-transparent { background-color: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 10px; margin-bottom: 20px; }
        .emoji-solid-yellow { font-size: 110px; text-align: center; color: #FFFF00; }
        label { color: #FFFF00 !important; font-weight: bold !important; }
        </style>
        """, unsafe_allow_html=True)

    c_nav1, c_nav2 = st.columns([8, 1.2])
    with c_nav1:
        if st.button("⬅ VOLVER AL INICIO"):
            st.session_state.page = "home"; st.rerun()
    with c_nav2:
        if st.button("🔄 ACTUALIZAR"):
            st.cache_data.clear(); st.rerun()

    @st.cache_data(ttl=600)
    def load_data(url):
        try:
            csv_url = url.split('/edit')[0] + "/export?format=csv"
            res = requests.get(csv_url)
            return pd.read_csv(StringIO(res.text))
        except: return pd.DataFrame()

    df = load_data("https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit")
    df_coords = load_data("https://docs.google.com/spreadsheets/d/1L-WNzMEAmvdcqSm0gvpRSzNUE29hwvxk396Q8MwUfUo/edit")

    if not df.empty:
        # Limpieza base principal
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        # Limpieza ID Cliente (Quitar .0 si es flotante y espacios)
        df['Customer ID'] = df['Customer ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # Cabecera
        b2, b1 = get_base64('logo2.png'), get_base64('logo.png')
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b2}" height="60"><h1>NPS 2025</h1><img src="data:image/png;base64,{b1}" height="60"></div>', unsafe_allow_html=True)

        # Gráficos superiores
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig1 = px.pie(df[df['Primary Driver']!='N/A'], names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(title="1. Primary Driver Composition", paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            data_l = df[df['Primary Driver']!='N/A'].groupby('Primary Driver')['Score'].mean().reset_index()
            fig2 = px.line(data_l, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFFF00', textposition="top center", mode='markers+lines+text', texttemplate='%{y:.2f}')
            fig2.update_layout(title="2. Average Score Per Driver", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig2, use_container_width=True)

        # Filtros
        st.markdown("---")
        cf1, cf2 = st.columns(2)
        sel_driver = cf1.selectbox('Primary Driver:', ['All'] + sorted(df['Primary Driver'].unique().tolist()))
        sel_cat = cf2.multiselect('Category:', sorted(df['Category'].unique().tolist()), default=df['Category'].unique().tolist())
        
        df_filt = df.copy()
        if sel_driver != 'All': df_filt = df_filt[df_filt['Primary Driver'] == sel_driver]
        df_filt = df_filt[df_filt['Category'].isin(sel_cat)]

        # --- MAPA DE CALOR (ROBUSTO) ---
        st.markdown('<p style="color:#FFFF00; font-size:25px; font-weight:bold; margin-top:20px;">GEOGRAPHIC HEATMAP</p>', unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar por Código de Cliente:", placeholder="Escriba el ID...")

        if not df_coords.empty:
            # Limpieza base coordenadas (A: ID, B: Lon, C: Lat)
            df_c = df_coords.copy()
            df_c.columns = ['ID', 'Lon', 'Lat'] + list(df_c.columns[3:])
            df_c['ID'] = df_c['ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Cruce
            df_map = pd.merge(df_filt, df_c[['ID', 'Lon', 'Lat']], left_on='Customer ID', right_on='ID', how='inner')
            
            if busqueda:
                df_map = df_map[df_map['Customer ID'].str.contains(busqueda, case=False)]

            if not df_map.empty:
                df_map['Lat'] = pd.to_numeric(df_map['Lat'], errors='coerce')
                df_map['Lon'] = pd.to_numeric(df_map['Lon'], errors='coerce')
                df_map = df_map.dropna(subset=['Lat', 'Lon'])

                fig_map = px.density_mapbox(
                    df_map, lat='Lat', lon='Lon', z='Score', radius=20,
                    center=dict(lat=df_map['Lat'].mean(), lon=df_map['Lon'].mean()), zoom=10,
                    mapbox_style="open-street-map", # FONDO BLANCO
                    hover_name='Customer ID',
                    hover_data={'Category': True, 'Score': True, 'Lat': False, 'Lon': False},
                    color_continuous_scale=[[0, 'rgba(255,0,0,0)'], [0.1, 'rgba(255,0,0,0.5)'], [1, 'rgba(255,0,0,1)']] # ROJO
                )
                fig_map.update_layout(height=600, margin=dict(t=0, b=0, l=0, r=0), coloraxis_showscale=False)
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("Sin datos para mostrar en el mapa con los filtros actuales.")

        # --- CHOSEN COMMENTS ---
        st.markdown("---")
        st.markdown('<p style="color:#FFFF00; font-size:30px; font-weight:bold; text-align:center;">CHOSEN COMMENTS</p>', unsafe_allow_html=True)
        ct1, ct2, ct3 = st.columns(3)
        for i, c in enumerate([ct1, ct2, ct3]):
            with c:
                st.markdown('<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>', unsafe_allow_html=True)
                st.text_input(f"Secondary Driver {i+1}:", key=f"t_{i}")
                st.text_input("Cliente:", key=f"cl_{i}"); st.number_input("Score:", 0, 10, key=f"s_{i}")
                st.text_area("Comentario:", key=f"co_{i}", height=100)

# ==========================================
# VISTA 3: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("<style>.stApp { background-color: black; color: white; }</style>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER"): st.session_state.page = "home"; st.rerun()
    st.title("MONTHLY EVOLUTION")
    st.write("Cargando indicadores temporales...")
    # (Aquí iría tu lógica de Monthly Evolution que ya tenías)
