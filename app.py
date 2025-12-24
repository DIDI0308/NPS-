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
# VISTA 1: HOME (FONDO LOGO3.PNG)
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("MONTHLY EVOLUTION", use_container_width=True):
            st.session_state.page = "monthly"
            st.rerun()
    with col2:
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

# ==========================================
# VISTA 2: DASHBOARD (FONDO NEGRO / CURRENT MONTH)
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
            df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'], errors='coerce')
            df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
            df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
            df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
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
            fig1.update_layout(title={'text': "1. Primary Driver Composition", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color="white", size=14)), font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)
        with col_g2:
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='markers+lines+text', textfont=dict(color="white", size=14))
            fig2.update_layout(title={'text': "2. Average Score Per Primary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=None, tickfont=font_axes, gridcolor='#333333'), yaxis=dict(title=None, tickfont=font_axes, gridcolor='#333333'), font=dict(color="white") )
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1: selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
        with c_f2: selector_cat = st.multiselect('Category:', sorted([cat for cat in df['Category'].unique() if cat != 'N/A']), default=['Detractor', 'Passive', 'Promoter'])
        
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
                fig3.update_layout(title={'text':"3. Category Composition", 'x':0.5, 'xanchor': 'center', 'font': font_main}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(tickfont=font_axes), legend=dict(font=dict(color="white", size=12)), font=dict(color="white"), height=450)
                st.plotly_chart(fig3, use_container_width=True)
        with col_d2:
            if not df_sec.empty:
                data_vol = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00', textfont=dict(color="black", size=14))
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x':0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(title=None, tickfont=font_axes), font=dict(color="white"), height=450)
                st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if not df_sec.empty:
            data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
            fig5 = go.Figure()
            for i, row in data_score.reset_index(drop=True).iterrows():
                fig5.add_trace(go.Bar(x=[row['Label']], y=[6], marker=dict(color='rgba(255,255,255,0.05)', line=dict(color='rgba(255,255,255,0.4)', width=1.5)), width=0.6, showlegend=False, hoverinfo='skip'))
                fig5.add_trace(go.Bar(x=[row['Label']], y=[1.5], base=6, marker=dict(color='rgba(255,255,255,0.05)', line=dict(color='rgba(255,255,255,0.4)', width=1.5)), width=0.4, showlegend=False, hoverinfo='skip'))
                fig5.add_trace(go.Bar(x=[row['Label']], y=[2.5], base=7.5, marker=dict(color='rgba(255,255,255,0.05)', line=dict(color='rgba(255,255,255,0.4)', width=1.5)), width=0.2, showlegend=False, hoverinfo='skip'))
                fig5.add_trace(go.Bar(x=[row['Label']], y=[0.2], base=10, marker=dict(color='#888'), width=0.25, showlegend=False, hoverinfo='skip'))
                score = row['Score']
                if score > 0: fig5.add_trace(go.Bar(x=[row['Label']], y=[min(score, 6)], marker=dict(color='#FFCC00'), width=0.6, showlegend=False))
                if score > 6: fig5.add_trace(go.Bar(x=[row['Label']], y=[min(score-6, 1.5)], base=6, marker=dict(color='#FFCC00'), width=0.4, showlegend=False))
                if score > 7.5: fig5.add_trace(go.Bar(x=[row['Label']], y=[min(score-7.5, 2.5)], base=7.5, marker=dict(color='#FFCC00'), width=0.2, showlegend=False))
                fig5.add_annotation(x=row['Label'], y=10.5, text=f"<b>{score:.2f}</b>", showarrow=False, font=dict(color="white", size=15))
            fig5.update_layout(title={'text': "5. Avg Score by Secondary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, barmode='overlay', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=None, tickfont=font_axes, showgrid=False), yaxis=dict(visible=False, range=[0, 12]), height=650, margin=dict(b=100))
            st.plotly_chart(fig5, use_container_width=True)

        # --- SECCIÓN MAPA DE CALOR (BLANCO Y CON COD CLIENTE) ---
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        if not df_coords.empty and not df_filt3.empty:
            try:
                df_coords.columns = [str(c).strip() for c in df_coords.columns]
                id_col_coords = df_coords.columns[0]  
                lon_col = df_coords.columns[1]         
                lat_col = df_coords.columns[2]         
                
                df_filt3['Customer ID'] = df_filt3['Customer ID'].astype(str).str.strip()
                df_coords[id_col_coords] = df_coords[id_col_coords].astype(str).str.strip()

                df_map_final = pd.merge(df_filt3, df_coords, left_on='Customer ID', right_on=id_col_coords, how='inner')
                
                if not df_map_final.empty:
                    df_map_final[lat_col] = pd.to_numeric(df_map_final[lat_col], errors='coerce')
                    df_map_final[lon_col] = pd.to_numeric(df_map_final[lon_col], errors='coerce')
                    df_map_final = df_map_final.dropna(subset=[lat_col, lon_col])

                    # MAPA BLANCO DINÁMICO
                    fig_map = px.density_mapbox(
                        df_map_final, 
                        lat=lat_col, 
                        lon=lon_col, 
                        z='Score', 
                        radius=15,
                        center=dict(lat=df_map_final[lat_col].mean(), lon=df_map_final[lon_col].mean()), 
                        zoom=10,
                        mapbox_style="carto-darkmatter",
                        hover_data={'Customer ID': True, lat_col: False, lon_col: False, 'Score': True},
                        color_continuous_scale=[[0, 'rgba(255,255,255,0)'], [0.1, 'rgba(255,255,255,0.2)'], [1, 'rgba(255,255,255,1)']]
                    )
                    
                    fig_map.update_layout(
                        title={'text': "6. Customer Density Heatmap (White High Contrast)", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        font=dict(color="white"), 
                        height=700, 
                        margin=dict(t=50, b=10),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.warning("No se encontraron coincidencias para el mapa.")
            except Exception as e:
                st.error(f"Error en mapa: {e}")

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown('<p style="color:#FFFF00; font-size:35px; font-weight:bold; text-align:center;">CHOSEN COMMENTS</p>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        def render_dynamic_card(col, key_id, default_title):
            with col:
                st.markdown(f'<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>', unsafe_allow_html=True)
                st.text_input("Secondary Driver:", value=default_title, key=f"title_{key_id}")
                st.text_input("Cliente:", key=f"client_{key_id}"); st.number_input("Score:", min_value=0, max_value=10, step=1, key=f"score_{key_id}")
                st.text_area("Comentario:", key=f"comment_{key_id}", height=120); st.text_input("Camión / Unidad:", key=f"truck_{key_id}")
        render_dynamic_card(col_t1, "c1", "Secondary Driver 1:"); render_dynamic_card(col_t2, "c2", "Secondary Driver 2:"); render_dynamic_card(col_t3, "c3", "Secondary Driver 3:")
    else: st.warning("Cargando datos...")

# ==========================================
# VISTA 3: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("""
        <style>
        .stApp { background-color: black; color: white; }
        .header-banner { background-color: #FFFF00; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 10px; }
        .header-title { color: black !important; font-family: 'Arial Black', sans-serif; font-size: 28px; margin: 0; text-align: center; flex-grow: 1; }
        .section-banner { background-color: #FFFF00; color: black !important; padding: 4px 10px; border-radius: 5px; text-align: center; margin-top: 15px; margin-bottom: 15px; font-weight: bold; }
        .logo-img { height: 70px; }
        div.stButton > button { background-color: #FFFF00; color: black; border: None; font-weight: bold; }
        .stTextArea label {
            color: #FFFF00 !important;
            font-size: 22px !important; 
            font-weight: bold !important;
            border: 2px solid #FFFF00; 
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 10px;
        }
        .detractores-table { width: 100%; border-collapse: collapse; color: black; background-color: white; margin-bottom: 20px; }
        .detractores-table th { background-color: #1a3a4a; color: white; padding: 10px; border: 1px solid #ddd; font-size: 12px; }
        .detractores-table td { padding: 8px; border: 1px solid #ddd; text-align: center; font-size: 12px; color: black; }
        .detractores-table .text-col { text-align: left; background-color: #f9f9f9; width: 25%; font-weight: bold; }
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

    img_logo_izq, img_logo_der = get_base64('logo2.png'), get_base64('logo.png')
    st.markdown(f"""
        <div class="header-banner">
            <img src="data:image/png;base64,{img_logo_izq if img_logo_izq else ""}" class="logo-img">
            <h1 class="header-title">MONTHLY EVOLUTION</h1>
            <img src="data:image/png;base64,{img_logo_der if img_logo_der else ""}" class="logo-img">
        </div>
        """, unsafe_allow_html=True)

    def load_live_data_evolution(spreadsheet_url):
        try:
            base_url = spreadsheet_url.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), header=None)
            return df
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return pd.DataFrame()

    SHEET_URL_EVO = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"
    df_raw = load_live_data_evolution(SHEET_URL_EVO)

    def render_nps_block(df, row_start_idx, title_prefix):
        meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        y25_m = pd.to_numeric(df.iloc[row_start_idx, 3:15], errors='coerce').tolist()
        bu_m = pd.to_numeric(df.iloc[row_start_idx + 1, 3:15], errors='coerce').tolist()
        y24_m = pd.to_numeric(df.iloc[row_start_idx + 2, 3:15], errors='coerce').tolist()
        val_ytd_25, val_ytd_bu, val_ytd_24 = pd.to_numeric(df.iloc[row_start_idx, 2], errors='coerce'), pd.to_numeric(df.iloc[row_start_idx + 1, 2], errors='coerce'), pd.to_numeric(df.iloc[row_start_idx + 2, 2], errors='coerce')
        label_25, label_bu, label_24 = str(df.iloc[row_start_idx, 1]), str(df.iloc[row_start_idx + 1, 1]), str(df.iloc[row_start_idx + 2, 1])
        valid_data = [i for i, v in enumerate(y25_m) if pd.notnull(v) and v != 0]
        last_idx = valid_data[-1] if valid_data else 0
        mes_txt = meses[last_idx]
        st.markdown(f"""<div class="section-banner"><h2 style='color: black; margin: 0; font-size: 19px;'>
                    {title_prefix} | {int(y25_m[last_idx])} {mes_txt} – {int(y24_m[last_idx])} LY {int(bu_m[last_idx])} BGT ({int(val_ytd_bu)}) | {int(val_ytd_25)} YTD vs {int(val_ytd_bu)} BGT YTD</h2></div>""", unsafe_allow_html=True)
        all_vals = [x for x in (y25_m + bu_m + y24_m) if pd.notnull(x)]
        max_l, min_l = max(all_vals) if all_vals else 100, min(all_vals) if all_vals else 0
        col_a, col_b = st.columns([3, 1.2])
        with col_a:
            fig_l = go.Figure()
            fig_l.add_trace(go.Scatter(x=meses, y=y25_m, mode='markers+lines+text', name=label_25, line=dict(color='#FFFF00', width=4), text=y25_m, textposition="top center", textfont=dict(color="white")))
            fig_l.add_trace(go.Scatter(x=meses, y=bu_m, mode='lines', name=label_bu, line=dict(color='#FFD700', width=2, dash='dash')))
            fig_l.add_trace(go.Scatter(x=meses, y=y24_m, mode='markers+lines+text', name=label_24, line=dict(color='#F4D03F', width=2), text=y24_m, textposition="bottom center", textfont=dict(color="white")))
            fig_l.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False, range=[min_l - 15, max_l + 25]), legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center", font=dict(color="white")), height=500, margin=dict(t=50))
            st.plotly_chart(fig_l, use_container_width=True)
        with col_b:
            fig_b = go.Figure()
            fig_b.add_trace(go.Bar(x=[label_24, label_bu, label_25], y=[val_ytd_24, val_ytd_bu, val_ytd_25], text=[f"{val_ytd_24}", f"{val_ytd_bu}", f"{val_ytd_25}"], textposition='auto', marker_color=['#F4D03F', '#FFD700', '#FFFF00'], width=0.6, textfont=dict(color="black", size=14, family="Arial Black")))
            y_t = max(val_ytd_25, val_ytd_bu, val_ytd_24) + 15
            p25, p24 = ((val_ytd_25 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0, ((val_ytd_24 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
            fig_b.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_t} L 2,{y_t} L 2,{val_ytd_25}", line=dict(color="white", width=2))
            fig_b.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_t} L 0,{y_t} L 0,{val_ytd_24}", line=dict(color="white", width=2))
            fig_b.add_annotation(x=1.5, y=y_t, text=f"<b>{p25:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p25 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)
            fig_b.add_annotation(x=0.5, y=y_t, text=f"<b>{p24:+.1f}%</b>", showarrow=False, bgcolor="#00FF00" if p24 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)
            fig_b.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False, range=[0, y_t + 30]), height=500, margin=dict(t=50))
            st.plotly_chart(fig_b, use_container_width=True)

    if not df_raw.empty:
        render_nps_block(df_raw, 2, "NPS CD EL ALTO")
        render_nps_block(df_raw, 7, "NPS EA")
        render_nps_block(df_raw, 11, "NPS LP")
        st.markdown('<div class="section-banner">DETRACTORS </div>', unsafe_allow_html=True)
        rows_det, months = [18, 20, 22], ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        table_html = '<table class="detractores-table"><thead><tr><th>Secondary Driver</th>'
        for m in months: table_html += f'<th>{m}</th>'
        table_html += '</tr></thead><tbody>'
        for r in rows_det:
            table_html += f'<tr><td class="text-col">{str(df_raw.iloc[r, 0])}</td>'
            for c in range(3, 15): table_html += f'<td>{df_raw.iloc[r, c] if pd.notnull(df_raw.iloc[r, c]) else "-"}</td>'
            table_html += '</tr>'
        st.markdown(table_html + '</tbody></table>', unsafe_allow_html=True)
        col_a1, col_a2, col_a3 = st.columns(3)
        for idx, col in zip([18, 20, 22], [col_a1, col_a2, col_a3]):
            val_ytd, txt_orig = df_raw.iloc[idx, 2], str(df_raw.iloc[idx, 0])
            palabras = txt_orig.split()
            mitad = len(palabras) // 2
            txt_form = "<br>".join([" ".join(palabras[:mitad]), " ".join(palabras[mitad:])])
            fig_ring = go.Figure(go.Pie(values=[1], hole=0.8, marker=dict(colors=['rgba(0,0,0,0)'], line=dict(color='#FFFF00', width=6)), showlegend=False, hoverinfo='none'))
            fig_ring.add_annotation(text=f"<b>{val_ytd}</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="white", size=45, family="Arial Black"))
            fig_ring.add_annotation(text=f"<b>{txt_form}</b>", x=0.5, y=-0.25, showarrow=False, font=dict(color="white", size=14), align='center', xref="paper", yref="paper")
            fig_ring.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=100, l=10, r=10), height=320)
            col.plotly_chart(fig_ring, use_container_width=True)
        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App", key="c1_m")
        with c2: st.text_area("Plan de Acción", height=150, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.", key="c2_m")
        with c3: st.text_area("Key KPIs", height=150, value="• Canjes\n• Rechazo\n• On time", key="c3_m")
