import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap

# Configuración de la página
st.set_page_config(page_title="Dashboard NPS", layout="wide")

# Estilos CSS para las tarjetas (Mantiene tu diseño original)
st.markdown("""
    <style>
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #31333F;
    }
    .emoji {
        font-size: 80px;
        text-align: center;
        color: #FFD700;
        line-height: 1;
        margin-bottom: 10px;
    }
    .header-naranja {
        background-color: #FF8C00;
        color: white;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. CARGA Y LIMPIEZA DE DATOS
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
    df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
    df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    df['Mes_Nombre'] = df['Survey Completed Date'].dt.month_name()
    return df

df = load_data()

# ==========================================
# 2. GRÁFICAS ESTÁTICAS (RESUMEN GLOBAL)
# ==========================================
st.title("DASHBOARD INTERACTIVO NPS")

col_global1, col_global2 = st.columns(2)

with col_global1:
    st.subheader("Primary Driver Composition")
    data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
    fig_anillo = px.pie(data_anillo, values='Customer ID', names='Primary Driver', 
                        hole=0.5, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D', '#F4D03F'])
    st.plotly_chart(fig_anillo, use_container_width=True)

with col_global2:
    st.subheader("Average Score Per Primary Driver")
    data_lineas_global = df.groupby('Primary Driver')['Score'].mean().sort_values(ascending=False).reset_index()
    fig_lineas_global = px.line(data_lineas_global, x='Primary Driver', y='Score', markers=True)
    fig_lineas_global.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'))
    fig_lineas_global.update_yaxes(range=[6, 10])
    st.plotly_chart(fig_lineas_global, use_container_width=True)

st.divider()

# ==========================================
# 3. PANEL INTERACTIVO (FILTROS SIDEBAR)
# ==========================================
st.sidebar.header("Filtros del Panel")
opciones_driver = ['All'] + sorted(df['Primary Driver'].unique().tolist())
selector_driver = st.sidebar.selectbox("Primary Driver:", opciones_driver)

opciones_cat = sorted([cat for cat in df['Category'].unique().tolist() if cat != 'N/A'])
selector_cat = st.sidebar.multiselect("Category:", opciones_cat, default=opciones_cat)

# Lógica de filtrado
df_filt = df.copy()
if selector_driver != 'All':
    df_filt = df_filt[df_filt['Primary Driver'] == selector_driver]

df_sec = df_filt[df_filt['Category'].isin(selector_cat)].copy()

# Renderizado de Gráficas Dinámicas
col_din1, col_din2, col_din3 = st.columns(3)

with col_din1:
    st.markdown("### Category Composition")
    df_visual_cat = df_filt[df_filt['Category'] != 'N/A']
    conteo_cat = df_visual_cat['Category'].value_counts(normalize=True).reset_index()
    conteo_cat.columns = ['Category', 'Percentage']
    
    # Mapeo de colores original
    color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
    
    fig_nps = px.bar(conteo_cat, x=['Composition %'], y='Percentage', color='Category',
                     color_discrete_map=color_map, barmode='stack')
    fig_nps.update_layout(yaxis_tickformat='.1%')
    st.plotly_chart(fig_nps, use_container_width=True)

with col_din2:
    st.markdown("### Volume by Secondary Driver")
    if not df_sec.empty:
        data_count_sec = df_sec['Secondary Driver'].value_counts().sort_values(ascending=True).reset_index()
        fig_vol = px.bar(data_count_sec, x='count', y='Secondary Driver', orientation='h',
                         color_discrete_sequence=['#FFD700'])
        st.plotly_chart(fig_vol, use_container_width=True)

with col_din3:
    st.markdown("### Avg Score by Secondary Driver")
    if not df_sec.empty:
        data_score_sec = df_sec.groupby('Secondary Driver')['Score'].mean().sort_values(ascending=False).reset_index()
        v_min, v_max = data_score_sec['Score'].min(), data_score_sec['Score'].max()
        
        fig_score = px.bar(data_score_sec, x='Secondary Driver', y='Score',
                           color_discrete_sequence=['#F4D03F'])
        fig_score.update_yaxes(range=[max(0, v_min - 0.4), min(10, v_max + 0.4)])
        st.plotly_chart(fig_score, use_container_width=True)

# ==========================================
# 4. SECCIÓN: COMMENTS CHOSEN (TARJETAS)
# ==========================================
st.divider()
st.header("COMMENTS CHOSEN")

col_t1, col_t2, col_t3 = st.columns(3)

def render_tarjeta(col, key_suffix, titulo_default):
    with col:
        st.markdown(f"""
            <div class="card">
                <div class="emoji">☹</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Streamlit no permite inputs dentro de HTML directamente, 
        # así que usamos el componente st.text_input con CSS
        driver_title = st.text_input("Driver:", value=titulo_default, key=f"header_{key_suffix}")
        st.markdown(f"<div class='header-naranja'>{driver_title}</div>", unsafe_allow_html=True)
        
        st.text_input("Cliente:", key=f"cli_{key_suffix}")
        st.number_input("Score:", min_value=0, max_value=10, key=f"sco_{key_suffix}")
        st.text_area("Comentario:", key=f"com_{key_suffix}", height=100)
        st.text_input("Camión:", key=f"cam_{key_suffix}")

render_tarjeta(col_t1, "1", "Secondary Driver 1:")
render_tarjeta(col_t2, "2", "Secondary Driver 2:")
render_tarjeta(col_t3, "3", "Secondary Driver 3:")
