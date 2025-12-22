import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# --- FUNCIONES DE UTILIDAD ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_data(ttl=300)
def load_data_google_sheets(spreadsheet_url):
    try:
        # Transformamos el link de edición a link de exportación CSV
        csv_url = spreadsheet_url.replace('/edit?usp=sharing', '/export?format=csv')
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leer el CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Limpieza de datos (basada en tu estructura anterior)
        df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'], errors='coerce')
        df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
        df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
        df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
        df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# URL de tu hoja de Google
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?usp=sharing"

# --- MANEJO DE ESTADO DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

# --- VISTA 1: HOME (FONDO LOGO3.PNG) ---
if st.session_state.page == "home":
    bin_str = get_base64('logo3.png')
    style_home = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str if bin_str else ''}");
        background-size: cover; background-position: center;
        overflow: hidden; height: 100vh; width: 100vw;
    }}
    header {{visibility: hidden;}}
    .block-container {{padding: 0 !important;}}
    .main-title {{
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: white; font-size: 4rem; font-weight: 800; text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8); z-index: 1000; letter-spacing: 2px;
    }}
    .stHorizontalBlock {{
        position: fixed; bottom: 10%; left: 50%; transform: translateX(-50%);
        width: 50% !important; z-index: 1001;
    }}
    div.stButton > button {{
        background-color: #FFFF00 !important; color: black !important;
        font-weight: bold !important; font-size: 18px !important;
        border: none !important; padding: 15px 30px !important;
        border-radius: 10px !important; box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }}
    </style>
    '''
    st.markdown(style_home, unsafe_allow_html=True)
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.toast("Aún trabajando...")
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

# --- VISTA 2: DASHBOARD (FONDO NEGRO) ---
elif st.session_state.page == "dashboard":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; overflow: auto !important; }
        div[data-testid="stButton"] button[kind="secondary"] {
            background-color: #FFFF00 !important; color: #000000 !important;
            border: none !important; font-weight: bold !important; padding: 0.5rem 1rem !important;
        }
        .banner-amarillo {
            background-color: #FFFF00; padding: 15px; display: flex;
            justify-content: space-between; align-items: center;
            border-radius: 5px; margin-top: 10px; margin-bottom: 25px;
        }
        .titulo-texto { text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }
        .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }
        .card-transparent { background-color: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 10px; margin-bottom: 20px; color: #FFFFFF; }
        .emoji-solid-yellow { font-size: 110px; text-align: center; color: #FFFF00; text-shadow: 0 0 0 #FFFF00; line-height: 1; margin-bottom: 15px; display: block; }
        label { color: #FFFF00 !important; font-weight: bold !important; }
        .stTextInput input, .stTextArea textarea, .stNumberInput input { background-color: #1A1A1A !important; color: white !important; border: 1px solid #333 !important; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO", key="back_btn"):
        st.session_state.page = "home"
        st.rerun()

    # Carga de datos desde Google Sheets
    df = load_data_google_sheets(SHEET_URL)

    # HEADER
    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    logo2_html = f'<img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;">' if b64_logo2 else ""
    logo_html = f'<img src="data:image/png;base64,{b64_logo}" style="max-height:80px;">' if b64_logo else ""
    st.markdown(f'<div class="banner-amarillo">{logo2_html}<div class="titulo-texto"><h1>NPS 2025</h1></div>{logo_html}</div>', unsafe_allow_html=True)

    if not df.empty:
        font_main = dict(color="white", size=22)
        font_axes = dict(color="white", size=14)

        # GRÁFICAS GLOBALES
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()

        with col_g1:
            data_anillo = df_global.groupby('Primary Driver').size().reset_index(name='count')
            fig1 = px.pie(data_anillo, values='count', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(title={'text': "1. Primary Driver Composition", 'x': 0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="white", size=14)), font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text', textfont=dict(color="white", size=14))
            fig2.update_layout(title={'text': "2. Average Score Per Primary Driver", 'x': 0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=None, tickfont=font_axes, gridcolor='#333333'), yaxis=dict(title=None, tickfont=font_axes, gridcolor='#333333'), font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

        # PANEL INTERACTIVO
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
        with c_f2:
            opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
            selector_cat = st.multiselect('Category:', opciones_cat, default=opciones_cat)

        df_filt3 = df.copy()
        if selector_driver != 'All': df_filt3 = df_filt3[df_filt3['Primary Driver'] == selector_driver]
        df_sec = df_filt3[df_filt3['Category'].isin(selector_cat)].copy()

        col_d1, col_d2 = st.columns([1, 2])
        with col_d1:
            df_visual_cat = df_filt3[df_filt3['Category'] != 'N/A']
            if not df_visual_cat.empty:
                conteo_cat = df_visual_cat['Category'].value_counts(normalize=True) * 100
                orden = ['Detractor', 'Passive', 'Promoter']
                color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
                fig3 = go.Figure()
                for cat in orden:
                    val = conteo_cat.get(cat, 0)
                    fig3.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else "", textfont=dict(color="white")))
                fig3.update_layout(title={'text':"3. Category Composition", 'x':0.5, 'font': font_main}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickfont=font_axes), legend=dict(font=dict(color="white", size=12)), font=dict(color="white"), height=450)
                st.plotly_chart(fig3, use_container_width=True)

        with col_d2:
            if not df_sec.empty:
                data_vol = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00', textfont=dict(color="black", size=14))
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x':0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(title=None, tickfont=font_axes), font=dict(color="white"), height=450)
                st.plotly_chart(fig4, use_container_width=True)

        # SCORE PROMEDIO
        st.markdown("<br>", unsafe_allow_html=True)
        if not df_sec.empty:
            data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
            fig5 = px.bar(data_score, x='Label', y='Score', text=data_score['Score'].map('{:.2f}'.format))
            fig5.update_traces(marker_color='#FFD700', textposition='outside', textfont=dict(color="white", size=14))
            fig5.update_layout(title={'text': "5. Avg Score by Secondary Driver", 'x':0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=None, tickfont=font_axes), yaxis=dict(title=None, tickfont=font_axes, gridcolor='#333333'), font=dict(color="white"), height=500)
            st.plotly_chart(fig5, use_container_width=True)

        # COMMENTS CHOSEN
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown('<p style="color:#FFFF00; font-size:35px; font-weight:bold; text-align:center;">COMMENTS CHOSEN</p>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)

        def render_dynamic_card(col, key_id, default_title):
            with col:
                st.markdown(f'<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>', unsafe_allow_html=True)
                st.text_input("Secondary Driver:", value=default_title, key=f"title_{key_id}")
                st.text_input("Cliente:", key=f"client_{key_id}")
                st.number_input("Score:", min_value=0, max_value=10, step=1, key=f"score_{key_id}")
                st.text_area("Comentario:", key=f"comment_{key_id}", height=120)
                st.text_input("Camión / Unidad:", key=f"truck_{key_id}")

        render_dynamic_card(col_t1, "c1", "Secondary Driver 1:")
        render_dynamic_card(col_t2, "c2", "Secondary Driver 2:")
        render_dynamic_card(col_t3, "c3", "Secondary Driver 3:")
    else:
        st.warning("No se encontraron datos en la hoja de Google Sheets.")
