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
    except:
        return None
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
        overflow: hidden; 
        height: 100vh;
        width: 100vw;
    }}
    header {{visibility: hidden;}}
    .block-container {{padding: 0 !important;}}
    .main-title {{
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        color: white; font-size: 4rem; font-weight: 800;
        text-align: center; width: 100%;
        text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        z-index: 1000; letter-spacing: 2px;
    }}
    .stHorizontalBlock {{
        position: fixed;
        bottom: 10%; left: 50%;
        transform: translateX(-50%);
        width: 50% !important;
        z-index: 1001;
    }}
    div.stButton > button {{
        background-color: #FFFF00 !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 10px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }}
    </style>
    '''
    st.markdown(style_home, unsafe_allow_html=True)
    st.markdown('<div class="main-title">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.page = "monthly"
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with col3:
        if st.button("EA / LP", use_container_width=True):
            st.session_state.page = "ea_lp"
            st.rerun()

# ==========================================
# VISTA 2: DASHBOARD (CURRENT MONTH)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; overflow: auto !important; }
        div[data-testid="stButton"] button { background-color: #FFFF00 !important; color: #000000 !important; border: none !important; font-weight: bold !important; padding: 0.5rem 1rem !important; }
        .banner-amarillo { background-color: #FFFF00; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-top: 10px; margin-bottom: 25px; }
        .titulo-texto { text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }
        .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }
        .card-transparent { background-color: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 10px; margin-bottom: 20px; color: #FFFFFF; }
        .emoji-solid-yellow { font-size: 110px; text-align: center; color: #FFFF00; text-shadow: 0 0 0 #FFFF00; line-height: 1; margin-bottom: 15px; display: block; }
        label { color: #FFFF00 !important; font-weight: bold !important; }
        .stTextInput input, .stTextArea textarea, .stNumberInput input { background-color: #1A1A1A !important; color: white !important; border: 1px solid #333 !important; }
        </style>
        """, unsafe_allow_html=True)

    c_nav1, c_nav2 = st.columns([8, 1.2])
    with c_nav1:
        if st.button("⬅ VOLVER AL INICIO", key="back_btn"):
            st.session_state.page = "home"
            st.rerun()
    with c_nav2:
        if st.button("🔄 ACTUALIZAR", key="refresh_dash"):
            st.cache_data.clear()
            st.rerun()

    @st.cache_data(ttl=600)
    def load_data_from_sheets(url):
        try:
            base_url = url.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv"
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            
            if 'Survey Completed Date' in df.columns:
                df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'], errors='coerce')
            for col in ['Primary Driver', 'Secondary Driver', 'Category']:
                if col in df.columns:
                    df[col] = df[col].astype(str).replace('nan', 'N/A')
            if 'Score' in df.columns:
                df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Error cargando datos de Sheets: {e}")
            return pd.DataFrame()

    SHEET_URL_CURRENT = "https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit?usp=sharing"
    SHEET_URL_MAP = "https://docs.google.com/spreadsheets/d/1L-WNzMEAmvdcqSm0gvpRSzNUE29hwvxk396Q8MwUfUo/edit?usp=sharing"
    
    df = load_data_from_sheets(SHEET_URL_CURRENT)
    df_coords = load_data_from_sheets(SHEET_URL_MAP)

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        font_main = dict(color="white", size=22)
        font_axes = dict(color="white", size=14)
        
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()
        
        with col_g1:
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(title={'text': "1. Primary Driver Composition", 'x': 0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="white")), font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='markers+lines+text')
            fig2.update_layout(title={'text': "2. Average Score Per Primary Driver", 'x': 0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(gridcolor='#333333'), yaxis=dict(gridcolor='#333333'), font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1: selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
        with c_f2: selector_cat = st.multiselect('Category:', sorted([cat for cat in df['Category'].unique() if cat != 'N/A']), default=['Detractor', 'Passive', 'Promoter'])
        
        df_filt3 = df.copy()
        if selector_driver != 'All': df_filt3 = df_filt3[df_filt3['Primary Driver'] == selector_driver]
        df_filt3 = df_filt3[df_filt3['Category'].isin(selector_cat)]

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
                    fig3.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else ""))
                fig3.update_layout(title={'text':"3. Category Composition", 'x':0.5, 'font': font_main}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450)
                st.plotly_chart(fig3, use_container_width=True)

        with col_d2:
            if not df_filt3.empty:
                data_vol = df_filt3['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00')
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x':0.5, 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450)
                st.plotly_chart(fig4, use_container_width=True)

        # Heatmap
        st.markdown('<p style="color:#FFFF00; font-size:25px; font-weight:bold; margin-top:20px;">GEOGRAPHIC HEATMAP</p>', unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar por Código de Cliente:", placeholder="ID...")
        if not df_coords.empty:
            df_c = df_coords.copy()
            df_c.columns = ['ID', 'Lon', 'Lat'] + list(df_c.columns[3:])
            df_c['ID'] = df_c['ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_filt_clean = df_filt3.copy()
            df_filt_clean['Customer ID'] = df_filt_clean['Customer ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_map = pd.merge(df_filt_clean, df_c[['ID', 'Lon', 'Lat']], left_on='Customer ID', right_on='ID', how='inner')
            if busqueda:
                df_map = df_map[df_map['Customer ID'].str.contains(busqueda, case=False)]
            if not df_map.empty:
                df_map['Lat'] = pd.to_numeric(df_map['Lat'], errors='coerce')
                df_map['Lon'] = pd.to_numeric(df_map['Lon'], errors='coerce')
                df_map = df_map.dropna(subset=['Lat', 'Lon'])
                fig_map = px.density_mapbox(df_map, lat='Lat', lon='Lon', z='Score', radius=20, center=dict(lat=df_map['Lat'].mean(), lon=df_map['Lon'].mean()), zoom=10, mapbox_style="open-street-map")
                fig_map.update_layout(height=600, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
                st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown('<p style="color:#FFFF00; font-size:35px; font-weight:bold; text-align:center;">CHOSEN COMMENTS</p>', unsafe_allow_html=True)
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
    else: st.warning("Cargando datos...")

# ==========================================
# VISTA 3: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("""
        <style>
        .stApp { background-color: black; color: white; }
        .header-banner { background-color: #FFFF00; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; }
        .header-title { color: black !important; font-family: 'Arial Black', sans-serif; font-size: 28px; margin: 0; text-align: center; flex-grow: 1; }
        .section-banner { background-color: #FFFF00; color: black !important; padding: 4px 10px; border-radius: 5px; text-align: center; margin-top: 15px; margin-bottom: 15px; font-weight: bold; }
        div.stButton > button { background-color: #FFFF00; color: black; border: None; font-weight: bold; }
        .detractores-table { width: 100%; border-collapse: collapse; color: black; background-color: white; margin-bottom: 20px; }
        .detractores-table th { background-color: #1a3a4a; color: white; padding: 10px; border: 1px solid #ddd; }
        .detractores-table td { padding: 8px; border: 1px solid #ddd; text-align: center; color: black; }
        </style>
        """, unsafe_allow_html=True)

    c_nav_m1, c_nav_m2 = st.columns([8, 1.2])
    with c_nav_m1:
        if st.button("⬅ VOLVER AL INICIO", key="back_btn_m"):
            st.session_state.page = "home"
            st.rerun()
    with c_nav_m2:
        if st.button("🔄 ACTUALIZAR", key="refresh_m"):
            st.cache_data.clear()
            st.rerun()

    def load_live_data_evolution(spreadsheet_url):
        try:
            base_url = spreadsheet_url.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
            response = requests.get(csv_url)
            df = pd.read_csv(StringIO(response.text), header=None)
            return df
        except: return pd.DataFrame()

    SHEET_URL_EVO = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"
    df_raw_evo = load_live_data_evolution(SHEET_URL_EVO)

    if not df_raw_evo.empty:
        def render_nps_block(df, row_start_idx, title_prefix):
            meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
            y25_m = pd.to_numeric(df.iloc[row_start_idx, 3:15], errors='coerce').tolist()
            bu_m = pd.to_numeric(df.iloc[row_start_idx + 1, 3:15], errors='coerce').tolist()
            y24_m = pd.to_numeric(df.iloc[row_start_idx + 2, 3:15], errors='coerce').tolist()
            val_ytd_25 = pd.to_numeric(df.iloc[row_start_idx, 2], errors='coerce')
            val_ytd_bu = pd.to_numeric(df.iloc[row_start_idx + 1, 2], errors='coerce')
            
            st.markdown(f'<div class="section-banner"><h2>{title_prefix} | YTD: {val_ytd_25} vs BGT: {val_ytd_bu}</h2></div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([3, 1.2])
            with col_a:
                fig_l = go.Figure()
                fig_l.add_trace(go.Scatter(x=meses, y=y25_m, mode='markers+lines+text', name="2025", line=dict(color='#FFFF00', width=4), text=y25_m, textposition="top center"))
                fig_l.add_trace(go.Scatter(x=meses, y=bu_m, mode='lines', name="Budget", line=dict(color='#FFD700', dash='dash')))
                fig_l.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=400)
                st.plotly_chart(fig_l, use_container_width=True)
            with col_b:
                fig_b = go.Figure(go.Bar(x=["LY", "BGT", "2025"], y=[0, val_ytd_bu, val_ytd_25], marker_color=['#F4D03F', '#FFD700', '#FFFF00']))
                fig_b.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=400)
                st.plotly_chart(fig_b, use_container_width=True)

        render_nps_block(df_raw_evo, 2, "NPS CD EL ALTO")
        render_nps_block(df_raw_evo, 7, "NPS EA")
        render_nps_block(df_raw_evo, 11, "NPS LP")

# ==========================================
# VISTA 4: EA / LP (SOLUCIÓN FINAL)
# ==========================================
elif st.session_state.page == "ea_lp":
    def get_data_absolute_new():
        try:
            u = "https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit?usp=sharing".split('/edit')[0]
            csv_url = f"{u}/export?format=csv&nocache={pd.Timestamp.now().timestamp()}"
            res = requests.get(csv_url)
            return pd.read_csv(StringIO(res.text))
        except: return pd.DataFrame()

    st.markdown("""
        <style>
        .stApp { background-color: #000000 !important; }
        div.stButton > button { background-color: #FFFF00 !important; color: black !important; font-weight: bold !important; border: 2px solid #FFFF00 !important; }
        .banner-ea-lp { background-color: #FFFF00; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

    c_nav1, c_nav2 = st.columns([8, 2])
    with c_nav1:
        if st.button("⬅ VOLVER AL INICIO", key="btn_v_home"):
            st.session_state.page = "home"
            st.rerun()
    with c_nav2:
        if st.button("🔄 ACTUALIZAR", key="btn_v_refresh"):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div class="banner-ea-lp"><h2 style="color:black; margin:0; font-family:Arial Black;">PERFORMANCE EA / LP</h2></div>', unsafe_allow_html=True)

    df_raw = get_data_absolute_new()

    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df_raw['Primary Driver'] = df_raw['Primary Driver'].astype(str).str.strip().str.upper()
        df_delivery = df_raw[df_raw['Primary Driver'] == 'DELIVERY'].copy()

        def clean_reg(x):
            x = str(x).upper()
            if 'ALTO' in x or 'EA' in x: return 'EA'
            if 'PAZ' in x or 'LP' in x: return 'LP'
            return 'OTRO'
        
        df_delivery['REG_GROUP'] = df_delivery['Sales Region'].apply(clean_reg)
        df_final = df_delivery[df_delivery['REG_GROUP'].isin(['EA', 'LP'])].copy()

        if not df_final.empty:
            col_izq, col_der = st.columns([1.5, 2.5])
            
            with col_izq:
                st.markdown('<p style="color:#FFFF00; font-size:18px; font-weight:bold; text-align:center;">CLIENT DISTRIBUTION</p>', unsafe_allow_html=True)
                df_plot = df_final.groupby(['Category', 'REG_GROUP'])['Customer ID'].count().reset_index()
                df_plot['Total_Barra'] = df_plot.groupby('Category')['Customer ID'].transform('sum')
                df_plot['Altura'] = (df_plot['Customer ID'] / df_plot['Total_Barra']) * 100

                fig = px.bar(
                    df_plot, x="Category", y="Altura", color="REG_GROUP", 
                    text="Customer ID", color_discrete_map={'EA': '#FFFF00', 'LP': '#DAA520'},
                    category_orders={"Category": ["Detractor", "Passive", "Promoter"]}, barmode="stack"
                )
                fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', height=450, font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True, key="dist_v4")
            
            with col_der:
                st.markdown('<p style="color:#FFFF00; font-size:18px; font-weight:bold; text-align:center;">SECONDARY DRIVER BY REGION</p>', unsafe_allow_html=True)
                df_horiz_data = df_final.groupby(['Secondary Driver', 'REG_GROUP']).size().reset_index(name='Cuenta')
                
                fig_horiz = px.bar(
                    df_horiz_data, y="Secondary Driver", x="Cuenta", color="REG_GROUP",
                    orientation='h', text="Cuenta", color_discrete_map={'EA': '#FFFF00', 'LP': '#CC9900'},
                    template="plotly_dark"
                )
                fig_horiz.update_layout(paper_bgcolor='black', plot_bgcolor='black', height=450)
                fig_horiz.update_traces(textposition='inside', textfont=dict(color="black", size=12))
                st.plotly_chart(fig_horiz, use_container_width=True, key="horiz_v4")
        else:
            st.warning("No data found for EA/LP in Delivery category.")
    else:
        st.error("Could not connect to the database (Google Sheets).")
