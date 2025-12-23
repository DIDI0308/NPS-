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
# VISTA 2: DASHBOARD (FONDO NEGRO)
# ==========================================
elif st.session_state.page == "dashboard":
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: #FFFFFF; overflow: auto !important; }
        div[data-testid="stButton"] button { background-color: #FFFF00 !important; color: #000000 !important; font-weight: bold !important; }
        .banner-amarillo { background-color: #FFFF00; padding: 15px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 25px; }
        .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; color: black; }
        .card-transparent { background-color: rgba(255, 255, 255, 0.02); border-radius: 15px; padding: 10px; margin-bottom: 20px; }
        .emoji-solid-yellow { font-size: 110px; text-align: center; color: #FFFF00; }
        label { color: #FFFF00 !important; font-weight: bold !important; }
        </style>
        """, unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    @st.cache_data
    def load_data():
        try:
            df = pd.read_excel('Base bruta dic.xlsx')
            df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
            df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
            df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
            df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
            df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
            return df
        except: return pd.DataFrame()

    df = load_data()
    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        font_main = dict(color="white", size=22)
        font_axes = dict(color="white", size=14)

        # --- GRÁFICAS GLOBALES ---
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()

        with col_g1:
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(title={'text': "1. Primary Driver Composition", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
            fig2.update_layout(title={'text': "2. Average Score Per Primary Driver", 'x': 0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        with c_f1: selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
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
                fig3 = go.Figure()
                color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
                for cat in ['Detractor', 'Passive', 'Promoter']:
                    val = conteo_cat.get(cat, 0)
                    fig3.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else ""))
                fig3.update_layout(title={'text':"3. Category Composition", 'x':0.5, 'xanchor': 'center', 'font': font_main}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                st.plotly_chart(fig3, use_container_width=True)

        with col_d2:
            if not df_sec.empty:
                data_vol = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00')
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x':0.5, 'xanchor': 'center', 'font': font_main}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                st.plotly_chart(fig4, use_container_width=True)

        # --- GRÁFICA 5: BOTELLAS DE CERVEZA (CENTREADA) ---
        st.markdown("<br>", unsafe_allow_html=True)
        if not df_sec.empty:
            data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
            
            fig5 = go.Figure()
            # "Líquido" de la cerveza (Barras amarillas)
            fig5.add_trace(go.Bar(
                x=data_score['Label'], y=data_score['Score'],
                marker_color='#FFFF00', width=0.4,
                text=data_score['Score'].map('{:.2f}'.format),
                textposition='outside', textfont=dict(color="white", size=14)
            ))
            
            # Contorno de la botella (Shapes SVG)
            for i in range(len(data_score)):
                w, h = 0.5, 10
                path = f"M {i-w/2},0 L {i+w/2},0 L {i+w/2},{h*0.7} L {i+w/6},{h*0.85} L {i+w/6},{h} L {i-w/6},{h} L {i-w/6},{h*0.85} L {i-w/2},{h*0.7} Z"
                fig5.add_shape(type="path", path=path, line_color="white", line_width=3, xref="x", yref="y")

            fig5.update_layout(
                title={'text': "5. Avg Score by Secondary Driver (Beer Fill)", 'x': 0.5, 'xanchor': 'center', 'font': font_main},
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title=None, showgrid=False), yaxis=dict(title=None, range=[0, 11], gridcolor='#333333'),
                font=dict(color="white"), height=600
            )
            st.plotly_chart(fig5, use_container_width=True)

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

# ==========================================
# VISTA 3: MONTHLY EVOLUTION (GOOGLE SHEET)
# ==========================================
elif st.session_state.page == "monthly":
    st.markdown("""<style>.stApp { background-color: black; color: white; }
        .header-banner { background-color: #FFFF00; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-radius: 5px; margin-bottom: 10px; }
        .header-title { color: black !important; font-family: 'Arial Black', sans-serif; font-size: 28px; margin: 0; text-align: center; flex-grow: 1; }
        .section-banner { background-color: #FFFF00; color: black !important; padding: 4px 10px; border-radius: 5px; text-align: center; margin-top: 15px; margin-bottom: 15px; font-weight: bold; }
        .stTextArea label { color: #FFFF00 !important; font-size: 22px !important; font-weight: bold !important; border: 2px solid #FFFF00; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-bottom: 10px; }
        .detractores-table { width: 100%; border-collapse: collapse; color: black; background-color: white; margin-bottom: 20px; }
        .detractores-table th { background-color: #1a3a4a; color: white; padding: 10px; border: 1px solid #ddd; }
        .detractores-table td { padding: 8px; border: 1px solid #ddd; text-align: center; color: black; }</style>""", unsafe_allow_html=True)

    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    img_logo_izq, img_logo_der = get_base64('logo2.png'), get_base64('logo.png')
    st.markdown(f'<div class="header-banner"><img src="data:image/png;base64,{img_logo_izq if img_logo_izq else ""}" style="height:70px;"><h1 class="header-title">MONTHLY EVOLUTION</h1><img src="data:image/png;base64,{img_logo_der if img_logo_der else ""}" style="height:70px;"></div>', unsafe_allow_html=True)

    def load_live_data(spreadsheet_url):
        try:
            base_url = spreadsheet_url.split('/edit')[0]
            csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
            return pd.read_csv(StringIO(requests.get(csv_url).text), header=None)
        except: return pd.DataFrame()

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"
    df_raw = load_live_data(SHEET_URL)

    def render_nps_block(df, row_idx, prefix):
        meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        y25 = pd.to_numeric(df.iloc[row_idx, 3:15], errors='coerce').tolist()
        bu = pd.to_numeric(df.iloc[row_idx+1, 3:15], errors='coerce').tolist()
        y24 = pd.to_numeric(df.iloc[row_idx+2, 3:15], errors='coerce').tolist()
        ytd25, ytd_bu, ytd24 = df.iloc[row_idx, 2], df.iloc[row_idx+1, 2], df.iloc[row_idx+2, 2]
        
        last = [i for i, v in enumerate(y25) if pd.notnull(v) and v != 0][-1]
        st.markdown(f'<div class="section-banner"><h2 style="color:black;margin:0;font-size:19px;">{prefix} | {int(y25[last])} {meses[last]} – {int(y24[last])} LY {int(bu[last])} BGT ({int(ytd_bu)}) | {int(ytd25)} YTD vs {int(ytd_bu)} BGT YTD</h2></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1.2])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=meses, y=y25, mode='markers+lines+text', name="2025", line=dict(color='#FFFF00', width=4), text=y25, textposition="top center"))
            fig.add_trace(go.Scatter(x=meses, y=bu, mode='lines', name="Budget", line=dict(color='#FFD700', dash='dash')))
            fig.add_trace(go.Scatter(x=meses, y=y24, mode='markers+lines+text', name="2024", line=dict(color='#F4D03F'), text=y24, textposition="bottom center"))
            fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=500, margin=dict(t=30))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            figb = go.Figure(go.Bar(x=["2024", "Budget", "2025"], y=[ytd24, ytd_bu, ytd25], marker_color=['#F4D03F', '#FFD700', '#FFFF00']))
            figb.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), height=500)
            st.plotly_chart(figb, use_container_width=True)

    if not df_raw.empty:
        render_nps_block(df_raw, 2, "NPS CD EL ALTO")
        render_nps_block(df_raw, 7, "NPS EA")
        render_nps_block(df_raw, 11, "NPS LP")

        st.markdown('<div class="section-banner">DETRACTORS</div>', unsafe_allow_html=True)
        rows_det = [18, 20, 22]
        months = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
        table = '<table class="detractores-table"><thead><tr><th>Secondary Driver</th>' + "".join([f"<th>{m}</th>" for m in months]) + '</tr></thead><tbody>'
        for r in rows_det:
            table += f'<tr><td style="text-align:left;font-weight:bold;">{df_raw.iloc[r,0]}</td>' + "".join([f'<td>{df_raw.iloc[r,c] if pd.notnull(df_raw.iloc[r,c]) else "-"}</td>' for c in range(3,15)]) + '</tr>'
        st.markdown(table + '</tbody></table>', unsafe_allow_html=True)

        cols = st.columns(3)
        for i, r in enumerate([18, 20, 22]):
            val, txt = df_raw.iloc[r, 2], str(df_raw.iloc[r, 0])
            p = txt.split()
            fmt = "<br>".join([" ".join(p[:len(p)//2]), " ".join(p[len(p)//2:])])
            fig = go.Figure(go.Pie(values=[1], hole=0.8, marker=dict(colors=['rgba(0,0,0,0)'], line=dict(color='#FFFF00', width=6)), showlegend=False))
            fig.add_annotation(text=f"<b>{val}</b>", x=0.5, y=0.5, showarrow=False, font=dict(color="white", size=45))
            fig.add_annotation(text=f"<b>{fmt}</b>", x=0.5, y=-0.25, showarrow=False, font=dict(color="white", size=14), align='center')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=100, l=10, r=10), height=320)
            cols[i].plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1: st.text_area("Causas Raíz YTD", height=150, value="Top 5:\n• Equipos de Frío\n• Servicio Entrega\n• Bees App")
        with c2: st.text_area("Plan de Acción", height=150, value="• Recapacitación atención cliente.\n• Refuerzo Operadores Logísticos.")
        with c3: st.text_area("Key KPIs", height=150, value="• Canjes\n• Rechazo\n• On time")
