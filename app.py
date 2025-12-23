import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS CD EL ALTO Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_live_data(spreadsheet_url):
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

SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # 1. PROCESAMIENTO DE DATOS MENSUALES (Filas 3-5, Columnas D-O)
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    y25_mensual = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    y24_mensual = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()
    bgt_mensual = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()

    # 2. PROCESAMIENTO DE DATOS YTD (Columnas B y C)
    val_ytd_25 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_ytd_bu = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_ytd_24 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')

    # 3. LÓGICA PARA EL TÍTULO DINÁMICO (MES ACTUAL)
    # Buscamos el último mes que tiene datos en 2025
    idx_actual = 0
    for i, v in enumerate(y25_mensual):
        if not pd.isna(v) and v != 0:
            idx_actual = i
    
    mes_actual_txt = meses_nombres[idx_actual]
    val_mes_actual_25 = y25_mensual[idx_actual]
    val_mes_actual_24 = y24_mensual[idx_actual]
    val_mes_actual_bu = bgt_mensual[idx_actual]

    # --- TÍTULO DINÁMICO SOLICITADO ---
    # NPS CD EL ALTO| (ytd 2025 mes actual) (MES ACTUAL)– (YTD 2024 MES ACTUAL) LY BGT (BU) | (YTD 2025) YTD vs (BU) BGT YTD
    st.markdown(f"""
        <h2 style='text-align: center; color: #FFFF00; font-size: 22px; padding: 20px;'>
            NPS CD EL ALTO | {val_mes_actual_25}% {mes_actual_txt} – {val_mes_actual_24}% LY BGT {val_mes_actual_bu}% | 
            {val_ytd_25}% YTD vs {val_ytd_bu}% BGT YTD
        </h2>
    """, unsafe_allow_html=True)

    # --- RENDERIZADO DE GRÁFICAS ---
    col_evol, col_ytd = st.columns([3, 1.2])

    with col_evol:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=y25_mensual, mode='lines+markers+text', name='2025', 
                                     line=dict(color='#FFFF00', width=4), text=y25_mensual, textposition="top center", 
                                     textfont=dict(color="white")))
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=bgt_mensual, mode='lines', name='BGT', 
                                     line=dict(color='#FFD700', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses_nombres, y=y24_mensual, mode='lines+markers+text', name='2024', 
                                     line=dict(color='#F4D03F', width=2), text=y24_mensual, textposition="bottom center", 
                                     textfont=dict(color="white")))
        
        fig_line.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False),
                              legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center", font=dict(color="white")),
                              height=500, margin=dict(t=30))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_ytd:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=['2024', 'BGT', '2025'], y=[val_ytd_24, val_ytd_bu, val_ytd_25],
                                 text=[f"{val_ytd_24}%", f"{val_ytd_bu}%", f"{val_ytd_25}%"], textposition='auto',
                                 marker_color=['#F4D03F', '#FFD700', '#FFFF00'], width=0.6,
                                 textfont=dict(color="black", size=14, family="Arial Black")))

        # Conexiones y Deltas
        y_top = max(val_ytd_25, val_ytd_bu, val_ytd_24) + 12
        pct_25 = ((val_ytd_25 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        pct_24 = ((val_ytd_24 / val_ytd_bu) - 1) * 100 if val_ytd_bu else 0
        
        c_25 = "#00FF00" if pct_25 >= 0 else "#FF0000"
        c_24 = "#00FF00" if pct_24 >= 0 else "#FF0000"

        fig_bar.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_top} L 2,{y_top} L 2,{val_ytd_25}", line=dict(color="white", width=2))
        fig_bar.add_shape(type="path", path=f"M 1,{val_ytd_bu} L 1,{y_top} L 0,{y_top} L 0,{val_ytd_24}", line=dict(color="white", width=2))

        fig_bar.add_annotation(x=1.5, y=y_top, text=f"<b>{pct_25:+.1f}%</b>", showarrow=False, bgcolor=c_25, font=dict(color="black"), bordercolor="white", borderpad=5)
        fig_bar.add_annotation(x=0.5, y=y_top, text=f"<b>{pct_24:+.1f}%</b>", showarrow=False, bgcolor=c_24, font=dict(color="black"), bordercolor="white", borderpad=5)

        fig_bar.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
                              xaxis=dict(showgrid=False, tickfont=dict(color="white")), yaxis=dict(visible=False, range=[0, y_top + 15]),
                              height=500, margin=dict(t=30))
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🔄 ACTUALIZAR DATOS"):
        st.rerun()
