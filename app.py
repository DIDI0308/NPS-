import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import textwrap

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = 'landing'

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- ESTILO CSS REFINADO ---
b64_bg = get_base64('logo3.png')

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) {{
        padding: 0px;
    }}
    .stApp {{ background-color: #000000; color: #FFFFFF; }}
    
    .landing-wrapper {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0;
        {" background-image: url('data:image/png;base64," + b64_bg + "');" if b64_bg else ""}
        background-size: cover; background-position: center; background-repeat: no-repeat;
    }}

    .landing-title {{
        position: fixed;
        top: 35%; left: 50%;
        transform: translate(-50%, -50%);
        width: 100%; text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 65px; font-weight: 900;
        color: #FFFFFF; text-shadow: 4px 4px 15px rgba(0,0,0,0.8);
        letter-spacing: 2px; z-index: 5; line-height: 1.1;
    }}

    /* BOTONES FIJOS POR POSICIÓN ABSOLUTA EN PANTALLA */
    /* Botón Izquierdo (Monthly Evolution) */
    div.stButton:nth-of-type(1) > button {{
        position: fixed !important;
        bottom: 15% !important;
        left: 20% !important;
        z-index: 1000 !important;
    }}

    /* Botón Derecho (Current Month) */
    div.stButton:nth-of-type(2) > button {{
        position: fixed !important;
        bottom: 15% !important;
        right: 20% !important;
        z-index: 1000 !important;
    }}

    div.stButton > button {{
        width: 320px !important;
        height: 80px !important;
        background-color: #FFFF00 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border-radius: 15px !important;
        border: 4px solid #000000 !important;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
        text-transform: uppercase;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover {{
        background-color: #FFEA00 !important;
        transform: scale(1.05) !important;
    }}

    /* Estilos dashboard interno */
    .banner-amarillo {{
        background-color: #FFFF00; padding: 15px; display: flex;
        justify-content: space-between; align-items: center;
        border-radius: 5px; margin: 20px;
    }}
    .titulo-texto {{ text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }}
    .titulo-texto h1 {{ margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }}
    .card-transparent {{
        background-color: rgba(255, 255, 255, 0.05);
        border: none; border-radius: 15px; padding: 15px; margin-bottom: 20px;
    }}
    .emoji-solid-yellow {{
        font-size: 110px; text-align: center; color: #FFFF00;
        text-shadow: 0 0 0 #FFFF00; line-height: 1; margin-bottom: 15px; display: block;
    }}
    label {{ color: #FFFF00 !important; font-weight: bold !important; }}
    .stTextInput input, .stTextArea textarea, .stNumberInput input {{
        background-color: #1A1A1A !important; color: white !important; border: 1px solid #333 !important;
    }}
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
        return pd.DataFrame(), "Mes"

df, mes_base = load_data()

# ==========================================
# VISTA: LANDING PAGE
# ==========================================
if st.session_state.page == 'landing':
    st.markdown(f'''
        <div class="landing-wrapper">
            <div class="landing-title">
                NET PROMOTER SCORE<br>PERFORMANCE
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Los botones ahora se renderizan directamente. El CSS se encarga de fijarlos.
    if st.button("MONTHLY EVOLUTION", key="btn_evo"):
        st.session_state.page = 'evolution'
        st.rerun()

    if st.button("CURRENT MONTH", key="btn_curr"):
        st.session_state.page = 'current'
        st.rerun()

# ==========================================
# VISTA: MONTHLY EVOLUTION
# ==========================================
elif st.session_state.page == 'evolution':
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()
    st.title("📈 MONTHLY EVOLUTION")
    st.info("Esta sección se encuentra en desarrollo.")

# ==========================================
# VISTA: CURRENT MONTH (ANÁLISIS COMPLETO)
# ==========================================
elif st.session_state.page == 'current':
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()

    b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
    if b64_logo and b64_logo2:
        st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

    if not df.empty:
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()

        with col_g1:
            st.markdown('<p style="font-size:22px; font-weight:bold; margin-left:20px;">1. Primary Driver Composition</p>', unsafe_allow_html=True)
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400, legend=dict(font=dict(color="white")))
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.markdown('<p style="font-size:22px; font-weight:bold;">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), yaxis=dict(gridcolor='#333333', title=None))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div style='margin: 0 20px;'><hr style='border: 1px solid #333;'></div>", unsafe_allow_html=True)
        
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']), key="sel_drive")
        with c_f2:
            opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
            selector_cat = st.multiselect('Category:', opciones_cat, default=opciones_cat, key="sel_cat")

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
                    fig3.add_trace(go.Bar(name=cat, x=['Composition %'], y=[val], marker_color=color_map[cat], text=f"{val:.1f}%" if val > 0 else "", textposition='auto'))
                fig3.update_layout(title={'text':"3. Category Composition", 'x':0.5, 'font':{'color':'white'}}, barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450, showlegend=True, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"), yaxis=dict(visible=False), margin=dict(t=50, b=100))
                st.plotly_chart(fig3, use_container_width=True)

        with col_d2:
            if not df_sec.empty:
                data_vol = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
                fig4 = px.bar(data_vol, x='count', y='Secondary Driver', orientation='h', text_auto=True)
                fig4.update_traces(marker_color='#FFEA00')
                fig4.update_layout(title={'text':"4. Volume by Secondary Driver", 'x':0.5, 'font':{'color':'white'}}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), xaxis=dict(visible=False), yaxis=dict(title=None), height=450)
                st.plotly_chart(fig4, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if not df_sec.empty:
            data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
            fig5 = px.bar(data_score, x='Label', y='Score', text=data_score['Score'].map('{:.2f}'.format))
            fig5.update_traces(marker_color='#FFD700', textposition='outside', textfont=dict(color='white', size=14))
            v_min = data_score['Score'].min()
            fig5.update_layout(title={'text': "5. Avg Score by Secondary Driver", 'x':0.5, 'font':{'color':'white', 'size':22}}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), yaxis=dict(range=[max(0, v_min - 0.6), 10.6], gridcolor='#333333', title=None), xaxis=dict(title=None), height=500)
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("<div style='margin: 0 20px;'><hr style='border: 1px solid #333;'><p style='color:#FFFF00; font-size:35px; font-weight:bold; text-align:center; margin-bottom:20px;'>CHOSEN COMMENTS </p></div>", unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        def render_dynamic_card(col, key_id, default_title):
            with col:
                st.markdown(f'''<div class="card-transparent"><div class="emoji-solid-yellow">☹</div></div>''', unsafe_allow_html=True)
                st.text_input("Secondary Driver:", value=default_title, key=f"title_{key_id}")
                st.text_input("Cliente:", key=f"client_{key_id}")
                st.number_input("Score:", min_value=0, max_value=10, step=1, key=f"score_{key_id}")
                st.text_area("Comentario:", key=f"comment_{key_id}", height=120)
                st.text_input("Camión / Unidad:", key=f"truck_{key_id}")
        render_dynamic_card(col_t1, "c1", "Secondary Driver 1:")
        render_dynamic_card(col_t2, "c2", "Secondary Driver 2:")
        render_dynamic_card(col_t3, "c3", "Secondary Driver 3:")
