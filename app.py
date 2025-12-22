import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Google Sheets Connector", layout="wide")

# --- ESTILOS PERSONALIZADOS (Banner Amarillo) ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #FFFFFF; }
    .stMetric { background-color: #1A1A1A; padding: 15px; border-radius: 10px; border: 1px solid #FFFF00; }
    div[data-testid="stMetricValue"] { color: #FFFF00 !important; }
    .banner {
        background-color: #FFFF00;
        color: #000000;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 25px;
    }
    </style>
    <div class="banner">
        <h1>CONECTOR DE DATOS: GOOGLE SHEETS</h1>
    </div>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE CARGA DE DATOS ---
@st.cache_data(ttl=60) # Actualiza cada 1 minuto
def cargar_hoja_google(url_compartida):
    try:
        # Transformar URL de edición a exportación CSV de la Hoja 1 (gid=0)
        base_url = url_compartida.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leer CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Limpieza básica de nombres de columnas
        df.columns = [c.strip() for c in df.columns]
        
        return df
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return None

# --- ENLACE DE TU HOJA ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?usp=sharing"

# --- CUERPO DE LA APP ---
st.write("### 📂 Vista previa de la Hoja 1")

df = cargar_hoja_google(URL_SHEET)

if df is not None:
    # 1. Mostrar métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", len(df))
    col2.metric("Columnas Detectadas", len(df.columns))
    
    if 'Score' in df.columns:
        promedio = pd.to_numeric(df['Score'], errors='coerce').mean()
        col3.metric("Promedio Score", f"{promedio:.2f}")

    # 2. Mostrar Tabla de Datos
    st.markdown("---")
    st.dataframe(df, use_container_width=True)

    # 3. Analizador de Columnas (Ayuda a depurar si fallan los nombres)
    with st.expander("🔍 Ver estructura técnica de las columnas"):
        st.write("Si tu otro código falla, asegúrate de que estos nombres sean exactos:")
        st.write(list(df.columns))

else:
    st.warning("No se pudieron cargar los datos. Verifica los permisos de compartir en Google Sheets.")
    st.info("El documento debe estar configurado como: 'Cualquier persona con el enlace puede leer'.")

# --- BOTÓN DE RECARGA ---
if st.button("🔄 Forzar actualización de datos"):
    st.cache_data.clear()
    st.rerun()
