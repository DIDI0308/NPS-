import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Dashboard 2025", layout="wide")

# --- ESTILO DARK MODE CON GRÁFICAS BLANCAS ---
st.markdown("""
    <style>
    /* Fondo general de la web en negro */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    /* Estilo de los contenedores de gráficas (Fondo Blanco) */
    .plot-container {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 1px solid #ddd;
        color: #000000;
    }
    /* Estilo de las tarjetas de comentarios */
    .card {
        background-color: #1A1A1A;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255,255,255,0.1);
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .emoji-grande { font-size: 80px; text-align: center; color: #FFD700; }
    .header-naranja {
        background-color: #FF8C00;
        color: white;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    /* Etiquetas de filtros en blanco */
    label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    # El archivo debe llamarse exactamente así en tu GitHub
    df = pd.read_excel('Base bruta dic.xlsx')
    df['Primary Driver'] = df['Primary Driver'].astype(str).replace('nan', 'N/A')
    df['Secondary Driver'] = df['Secondary Driver'].astype(str).replace('nan', 'N/A')
    df['Category'] = df['Category'].astype(str).replace('nan', 'N/A')
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0)
    df['Survey Completed Date'] = pd.to_datetime(df['Survey Completed Date'])
    return df

try:
    df = load_data()
    mes_actual = df['Survey Completed Date'].dt.month_name().iloc[0]
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

# --- TÍTULO PRINCIPAL ---
st.markdown(f"<h1 style='text-align: center; color: #FFD700; margin-bottom: 50px;'>NPS 2025 - {mes_actual}</h1>", unsafe_allow_html=True)

# --- 2. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Segmentación")
driver_list = ['All'] + sorted(df['Primary Driver'].unique().tolist())
driver_select = st.sidebar.selectbox("Primary Driver:", driver_list)

cat_options = sorted([c for c in df['Category'].unique().tolist() if c != 'N/A'])
cat_select = st.sidebar.multiselect("Categorías:", cat_options, default=cat_options)

# Filtrado de datos
df_filt = df if driver_select == 'All' else df[df['Primary Driver'] == driver_select]
df_sec = df_filt[df_filt['Category'].isin(cat_select)]

# --- 3. DISEÑO DE GRÁFICAS ---

# FILA 1: NPS y Global
col_top1, col_top2 = st.columns([1, 1.5])

with col_top1:
    st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
    df_vis = df_filt[df_filt['Category'] != 'N/A']
    conteo_cat = df_vis['Category'].value_counts(normalize=True).reset_index()
    conteo_cat.columns = ['Category', 'Percentage']
    fig_nps = px.bar(conteo_cat, x='Category', y='Percentage', color='Category',
                     color_discrete_map={'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'},
                     title="<b>Category Composition %</b>", template="plotly_white")
    st.plotly_chart(fig_nps, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_top2:
    st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
    data_lineas = df.groupby('Primary Driver')['Score'].mean().sort_values(ascending=False).reset_index()
    fig_lineas = px.line(data_lineas, x='Primary Driver', y='Score', markers=True,
                         title="<b>Average Score per Primary Driver (Global)</b>", template="plotly_white")
    fig_lineas.update_traces(line_color='#FF8C00', marker=dict(size=10))
    fig_lineas.update_layout(yaxis_range=[6, 10])
    st.plotly_chart(fig_lineas, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# FILA 2: Volume by Secondary Driver (Largo)
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
if not df_sec.empty:
    vol_data = df_sec['Secondary Driver'].value_counts().reset_index().sort_values(by='count')
    fig_vol = px.bar(vol_data, y='Secondary Driver', x='count', orientation='h', 
                     title="<b>Volume by Secondary Driver</b>", template="plotly_white",
                     color_discrete_sequence=['#FFD700'])
    st.plotly_chart(fig_vol, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# FILA 3: Avg Score by Secondary Driver (Abajo y Largo)
st.markdown("<div class='plot-container'>", unsafe_allow_html=True)
if not df_sec.empty:
    score_data = df_sec.groupby('Secondary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
    fig_score = px.bar(score_data, x='Secondary Driver', y='Score', 
                       title="<b>Average Score by Secondary Driver</b>", template="plotly_white",
                       color_discrete_sequence=['#FF8C00'])
    ymin = max(0, score_data['Score'].min() - 0.4)
    fig_score.update_layout(yaxis_range=[ymin, 10])
    st.plotly_chart(fig_score, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 4. SECCIÓN COMMENTS CHOSEN ---
st.divider()
st.markdown("<h2 style='text-align: center; color: #FFD700;'>☹ COMMENTS CHOSEN</h2>", unsafe_allow_html=True)
t1, t2, t3 = st.columns(3)

for i, col in enumerate([t1, t2, t3]):
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="emoji-grande">☹</div>
        </div>
        """, unsafe_allow_html=True)
        driver_title = st.text_input(f"Título {i+1}", f"Secondary Driver {i+1}", key=f"t{i}")
        st.markdown(f"<div class='header-naranja'>{driver_title}</div>", unsafe_allow_html=True)
        st.text_input("Cliente:", key=f"cli{i}")
        st.number_input("Score:", 0, 10, key=f"sc{i}")
        st.text_area("Comentario:", key=f"com{i}", height=120)
        st.text_input("Camión:", key=f"cam{i}")
