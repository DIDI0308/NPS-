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

# --- CONEXIÓN A GOOGLE SHEETS (HOJA 1) ---
@st.cache_data(ttl=60)
def load_data_google_sheets(spreadsheet_url):
    try:
        # Forzamos la descarga del CSV de la Hoja 1 (gid=0)
        base_url = spreadsheet_url.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv&gid=0"
        
        response = requests.get(csv_url)
        response.raise_for_status()
        
        df = pd.read_csv(StringIO(response.text))
        
        # --- LIMPIEZA FLEXIBLE DE COLUMNAS ---
        # Convertimos nombres de columnas a minúsculas y quitamos espacios para evitar errores
        df.columns = [c.strip() for c in df.columns]
        
        # Mapeo flexible (busca la columna que más se parezca)
        def find_col(target, columns):
            for c in columns:
                if target.lower() in c.lower(): return c
            return None

        col_date = find_col('Survey Completed Date', df.columns)
        col_primary = find_col('Primary Driver', df.columns)
        col_secondary = find_col('Secondary Driver', df.columns)
        col_category = find_col('Category', df.columns)
        col_score = find_col('Score', df.columns)

        # Si encuentra las columnas, las renombra a un estándar para el resto del código
        if col_date: df['Survey Completed Date'] = pd.to_datetime(df[col_date], errors='coerce')
        if col_primary: df['Primary Driver'] = df[col_primary].astype(str).replace('nan', 'N/A')
        if col_secondary: df['Secondary Driver'] = df[col_secondary].astype(str).replace('nan', 'N/A')
        if col_category: df['Category'] = df[col_category].astype(str).replace('nan', 'N/A')
        if col_score: df['Score'] = pd.to_numeric(df[col_score], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Error crítico: {e}")
        return pd.DataFrame()

# URL de tu hoja de Google
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?usp=sharing"

# --- LÓGICA DE NAVEGACIÓN ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    # (Mantener el código de la vista HOME igual que antes...)
    bin_str = get_base64('logo3.png')
    st.markdown(f'''<style>.stApp {{ background-image: url("data:image/png;base64,{bin_str if bin_str else ''}"); background-size: cover; }}</style>''', unsafe_allow_html=True)
    st.markdown('<div style="position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:4rem; font-weight:800; text-align:center; width:100%; text-shadow:4px 4px 15px black;">NET PROMOTER SCORE PERFORMANCE</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.button("MONTHLY EVOLUTION", use_container_width=True)
    with col2: 
        if st.button("CURRENT MONTH", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

elif st.session_state.page == "dashboard":
    # CSS DASHBOARD
    st.markdown("""<style>.stApp { background-color: black; color: white; } 
    div[data-testid="stButton"] button { background-color: #FFFF00 !important; color: black !important; font-weight: bold; }</style>""", unsafe_allow_html=True)
    
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = "home"
        st.rerun()

    df = load_data_google_sheets(SHEET_URL)

    if not df.empty:
        # Verificar si las columnas necesarias existen después del mapeo flexible
        required = ['Primary Driver', 'Score', 'Category']
        if all(col in df.columns for col in required):
            # --- AQUÍ VA TODO TU CÓDIGO DE GRÁFICAS (Mantenlo igual) ---
            st.success("Datos cargados de Google Sheets")
            st.dataframe(df.head(3)) # Mini vista previa para confirmar
            
            # (Insertar aquí las gráficas 1 a 5 que ya tienes configuradas)
            
        else:
            st.error("El archivo se leyó, pero faltan columnas clave.")
            st.write("Columnas detectadas en tu Excel:", list(df.columns))
    else:
        st.warning("No se pudo conectar. Verifica que el Google Sheet esté compartido como 'Cualquier persona con el enlace puede leer'.")
