import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS CD EL ALTO Dashboard", layout="wide")

# Estilo para fondo negro y texto blanco
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_live_data(spreadsheet_url):
    try:
        base_url = spreadsheet_url.split('/edit')[0]
        # Sincronización en tiempo real saltando el caché
        csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Leemos el CSV manteniendo los encabezados originales (A, B, C...)
        # Nota: Si tu CSV no tiene letras, Pandas usará la primera fila como nombres.
        df = pd.read_csv(StringIO(response.text))
        
        # Limpiamos nombres de columnas para evitar errores de espacios
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # --- MAPEADO DE COLUMNAS ---
    # Usamos los nombres de las columnas que mencionaste
    col_nombres = "B"
    col_ytd = "C"
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

    # --- EXTRACCIÓN DE DATOS (Filas 3, 4, 5 de Excel = Índices 1, 2, 3 en DataFrame con header) ---
    # Ajustamos los índices porque la primera fila del Excel se toma como encabezado
    y25_row = df_raw.iloc[1] # Fila 3 Excel
    bu_row = df_raw.iloc[2]  # Fila 4 Excel
    y24_row = df_raw.iloc[3] # Fila 5 Excel

    # Datos Mensuales (Gráfica de Líneas)
    y25_mensual = pd.to_numeric(y25_row[meses_nombres], errors='coerce').tolist()
    y24_mensual = pd.to_numeric(y24_row[meses_nombres], errors='coerce').tolist()
    bgt_mensual = pd.to_numeric(bu_row[meses_nombres], errors='coerce').tolist()

    # Datos YTD (Gráfica de Barras)
    val_ytd_25 = pd.to_numeric(y25_row[col_ytd], errors='coerce')
    val_ytd_bu = pd.to_numeric(bu_row[col_ytd], errors='coerce')
    val_ytd_24 = pd.to_numeric(y24_row[col_ytd], errors='coerce')
    
    label_25 = str(y25_row[col_nombres])
    label_bu = str(bu_row[col_nombres])
    label_24 = str(y24_row[col_nombres])

    # --- LÓGICA PARA TÍTULO DINÁMICO ---
    idx_actual = 0
    for i, v in enumerate(y25_mensual):
        if not pd.isna(v) and v != 0:
            idx_actual = i
    
    mes_txt = meses_nombres[idx_actual]
    v_ma_25 = int(y25_mensual[idx_actual]) if not pd.isna(y25_mensual[idx_actual]) else 0
    v_ma_24 = int(y24_mensual[idx_actual]) if not pd.isna(y24_mensual[idx_actual]) else 0
    v_ma_bu = int(bgt_mensual[idx_actual]) if not pd.isna(bgt_mensual[idx_actual]) else 0

    # TÍTULO SOLICITADO
    st.markdown(f"""
        <h2 style='text-align: center; color: #FFFF00; font-size: 20px; padding: 15px;'>
            NPS CD EL ALTO | {v_ma_25} {mes_txt} – {v_ma_24} LY BGT {v_ma_bu} | 
            {int(val_ytd_25)} YTD vs {int(val_ytd_bu)} BGT YTD
        </h2>
    """, unsafe_allow_html=True)

    # --- RENDERIZADO ---
    col_evol, col_ytd_graph = st.columns([3, 1.2])

    with col_evol:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=y25_mensual, mode='lines+markers+text', name=label_25, 
                                     line=dict(color='#FFFF00', width=4), text=y25_mensual, textposition="top center", 
                                     textfont=dict(color="white")))
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=bgt_mensual, mode='lines', name=label_bu, 
                                     line=dict(color='#FFD700', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=y24_mensual, mode='lines+markers+text', name=label_24, 
                                     line=dict(color='#F4D03F', width=2), text=y24_mensual, textposition="bottom center", 
                                     textfont=dict(color="white")))
        
        fig_line.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False),
                              legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
                              height=500)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_ytd_graph:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=[label_24, label_bu, label_25], y=[val_ytd_24, val_ytd_bu, val_ytd_25],
                                 text=[f"{val_ytd_24}%", f"{val_ytd_bu}%", f"{val_ytd_25}%"], textposition='auto',
                                 marker_color=['#F4D03F', '#FFD700', '#FFFF00'], width=0.6,
                                 textfont=dict(color="black", size=14, family="Arial Black")))

        y_top = max(val_ytd_25, val_ytd_bu, val_ytd_24) + 12
        p25 = ((val_ytd_25 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        p24 = ((val_ytd_24 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        
        # Conexiones rectas
        fig_bar.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_top} L 2,{y_top} L 2,{val_ytd_25}", line=dict(color="white", width=2))
        fig_bar.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_top} L 0,{y_top} L 0,{val_ytd_24}", line=dict(color="white", width=2))

        # Círculos informativos (Verde/Rojo)
        fig_bar.add_annotation(x=1.5, y=y_top, text=f"<b>{p25:+.1f}%</b>", showarrow=False, 
                               bgcolor="#00FF00" if p25 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)
        fig_bar.add_annotation(x=0.5, y=y_top, text=f"<b>{p24:+.1f}%</b>", showarrow=False, 
                               bgcolor="#00FF00" if p24 >= 0 else "#FF0000", font=dict(color="black"), bordercolor="white", borderpad=5)

        fig_bar.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False, range=[0, y_top + 15]),
                              height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🔄 ACTUALIZAR DATOS"):
        st.rerun()
