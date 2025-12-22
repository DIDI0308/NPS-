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

# --- ESTILO CSS REFINADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    .banner-amarillo {
        background-color: #FFFF00; padding: 15px; display: flex;
        justify-content: space-between; align-items: center;
        border-radius: 5px; margin-bottom: 25px;
    }
    .titulo-texto { text-align: center; flex-grow: 1; color: #000000; font-family: 'Arial Black', sans-serif; }
    .titulo-texto h1 { margin: 0; font-size: 50px; font-weight: 900; line-height: 1; }

    /* ESTILO TARJETAS DE COMENTARIOS (SIN MARGEN AMARILLO) */
    .card-transparent {
        background-color: rgba(255, 255, 255, 0.02);
        border: none; /* Eliminado el margen amarillo */
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 20px;
        color: #FFFFFF;
    }
    .emoji-solid-yellow {
        font-size: 110px; /* Tamaño aumentado */
        text-align: center;
        color: #FFFF00;
        /* Técnica para hacer la carita triste rellena de color */
        text-shadow: 0 0 0 #FFFF00; 
        line-height: 1;
        margin-bottom: 15px;
        display: block;
    }
    
    /* Ajuste de color de labels para fondo negro */
    label { color: #FFFF00 !important; font-weight: bold !important; }
    
    /* Inputs con fondo oscuro para legibilidad en negro */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #1A1A1A !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
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

# --- HEADER / BANNER ---
b64_logo2, b64_logo = get_base64('logo2.png'), get_base64('logo.png')
if b64_logo and b64_logo2:
    st.markdown(f'<div class="banner-amarillo"><img src="data:image/png;base64,{b64_logo2}" style="max-height:80px;"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div><img src="data:image/png;base64,{b64_logo}" style="max-height:80px;"></div>', unsafe_allow_html=True)

# --- GRÁFICAS GLOBALES ---
col_g1, col_g2 = st.columns(2)
df_global = df[df['Primary Driver'] != 'N/A'].copy() if not df.empty else pd.DataFrame()

if not df_global.empty:
    with col_g1:
        st.markdown('<p style="font-size:22px; font-weight:bold;">1. Primary Driver Composition</p>', unsafe_allow_html=True)
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

# --- PANEL INTERACTIVO ---
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
c_f1, c_f2 = st.columns(2)
if not df.empty:
    with c_f1:
        selector_driver = st.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
    with c_f2:
        opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
        selector_cat = st.multiselect('Category:', opciones_cat, default=opciones_cat)

    df_filt3 = df.copy()
    if selector_driver != 'All': df_filt3 = df_filt3[df_filt3['Primary Driver'] == selector_driver]
    df_sec = df_filt3[df_filt3['Category'].isin(selector_cat)].copy()

    # Fila de Composición y Volumen
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

    # --- FILA DINÁMICA B (SCORE PROMEDIO) ---
    st.markdown("<br>", unsafe_allow_html=True)
    if not df_sec.empty:
        data_score = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
        data_score['Label'] = data_score['Secondary Driver'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=15)))
        fig5 = px.bar(data_score, x='Label', y='Score', text=data_score['Score'].map('{:.2f}'.format))
        fig5.update_traces(marker_color='#FFD700', textposition='outside', textfont=dict(color='white', size=14))
        v_min = data_score['Score'].min()
        fig5.update_layout(title={'text': "5. Avg Score by Secondary Driver", 'x':0.5, 'font':{'color':'white', 'size':22}}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), yaxis=dict(range=[max(0, v_min - 0.6), 10.6], gridcolor='#333333', title=None), xaxis=dict(title=None), height=500)
        st.plotly_chart(fig5, use_container_width=True)

# ==========================================
# SECCIÓN: COMMENTS CHOSEN (TARJETAS LIMPIAS)
# ==========================================
st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
st.markdown('<p style="color:#FFFF00; font-size:35px; font-weight:bold; text-align:center; margin-bottom:20px;">COMMENTS CHOSEN</p>', unsafe_allow_html=True)

col_t1, col_t2, col_t3 = st.columns(3)

def render_dynamic_card(col, key_id, default_title):
    with col:
        st.markdown(f'''
            <div class="card-transparent">
                <div class="emoji-solid-yellow">☹</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Inputs para el usuario
        st.text_input("Secondary Driver:", value=default_title, key=f"title_{key_id}")
        st.text_input("Cliente:", key=f"client_{key_id}")
        st.number_input("Score:", min_value=0, max_value=10, step=1, key=f"score_{key_id}")
        st.text_area("Comentario:", key=f"comment_{key_id}", height=120)
        st.text_input("Camión / Unidad:", key=f"truck_{key_id}")

render_dynamic_card(col_t1, "c1", "Secondary Driver 1:")
render_dynamic_card(col_t2, "c2", "Secondary Driver 2:")
render_dynamic_card(col_t3, "c3", "Secondary Driver 3:")
