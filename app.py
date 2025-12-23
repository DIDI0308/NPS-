import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="NPS Performance Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    </style>
    """, unsafe_allow_html=True)

def load_live_data(spreadsheet_url):
    try:
        base_url = spreadsheet_url.split('/edit')[0]
        # Sincronización en tiempo real saltando el caché del navegador
        csv_url = f"{base_url}/export?format=csv&gid=0&cache_bust=" + str(pd.Timestamp.now().timestamp())
        response = requests.get(csv_url)
        response.raise_for_status()
        # Fila 3=índice 2, Fila 4=índice 3, Fila 5=índice 4
        df = pd.read_csv(StringIO(response.text), header=None)
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFzkoiDubO6E_m-bNMqk1QUl6JJgZ7uTB6si_WqmFHI/edit?gid=0#gid=0"

df_raw = load_live_data(SHEET_URL)

if not df_raw.empty:
    # 1. DATOS DE LÍNEAS (Filas 3-5, Columnas D-O)
    meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    y25_line = pd.to_numeric(df_raw.iloc[2, 3:15], errors='coerce').tolist()
    bgt_line = pd.to_numeric(df_raw.iloc[3, 3:15], errors='coerce').tolist()
    y24_line = pd.to_numeric(df_raw.iloc[4, 3:15], errors='coerce').tolist()

    # 2. DATOS DE BARRAS (Filas 3-5, Col B y C)
    val_25 = pd.to_numeric(df_raw.iloc[2, 2], errors='coerce')
    val_bu = pd.to_numeric(df_raw.iloc[3, 2], errors='coerce')
    val_24 = pd.to_numeric(df_raw.iloc[4, 2], errors='coerce')
    
    label_25 = str(df_raw.iloc[2, 1])
    label_bu = str(df_raw.iloc[3, 1])
    label_24 = str(df_raw.iloc[4, 1])

    # 3. CÁLCULO DE CRECIMIENTO EN %
    pct_25_vs_bu = ((val_25 / val_bu) - 1) * 100 if val_bu != 0 else 0
    pct_24_vs_bu = ((val_24 / val_bu) - 1) * 100 if val_bu != 0 else 0

    # --- RENDERIZADO ---
    col_evol, col_ytd = st.columns([3, 1.2])

    with col_evol:
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>NPS MONTHLY EVOLUTION</h3>", unsafe_allow_html=True)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=meses, y=y25_line, mode='lines+markers+text', name=label_25, line=dict(color='#FFFF00', width=4), text=y25_line, textposition="top center", textfont=dict(color="white")))
        fig_line.add_trace(go.Scatter(x=meses, y=bgt_line, mode='lines', name=label_bu, line=dict(color='#FFD700', width=2, dash='dash')))
        fig_line.add_trace(go.Scatter(x=meses, y=y24_line, mode='lines+markers+text', name=label_24, line=dict(color='#F4D03F', width=2), text=y24_line, textposition="bottom center", textfont=dict(color="white")))
        fig_line.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"), xaxis=dict(showgrid=False), yaxis=dict(visible=False), legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"), height=500)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_ytd:
        st.markdown("<h3 style='text-align: center; color: #FFFF00;'>YTD COMPARISON</h3>", unsafe_allow_html=True)
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=[label_24, label_bu, label_25],
            y=[val_24, val_bu, val_25],
            text=[f"{val_24}%", f"{val_bu}%", f"{val_25}%"],
            textposition='auto',
            marker_color=['#F4D03F', '#FFD700', '#FFFF00'],
            width=0.5,
            textfont=dict(color="black", size=14, family="Arial Black")
        ))

        # FLECHAS RECTAS QUE CONECTAN LAS BARRAS
        # Conexión BU -> 2025 (Horizontal al nivel del BU)
        fig_bar.add_annotation(
            x=label_25, y=val_bu, ax=label_bu, ay=val_bu,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="white"
        )
        # Círculo % en medio de BU y 2025
        fig_bar.add_annotation(
            x=1.5, y=val_bu, text=f"<b>{pct_25_vs_bu:+.1f}%</b>",
            showarrow=False, font=dict(color="black", size=11),
            bgcolor="#FFFF00", bordercolor="white", borderwidth=2, borderpad=6
        )

        # Conexión BU -> 2024 (Horizontal al nivel del BU)
        fig_bar.add_annotation(
            x=label_24, y=val_bu, ax=label_bu, ay=val_bu,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="white"
        )
        # Círculo % en medio de BU y 2024
        fig_bar.add_annotation(
            x=0.5, y=val_bu, text=f"<b>{pct_24_vs_bu:+.1f}%</b>",
            showarrow=False, font=dict(color="black", size=11),
            bgcolor="#F4D03F", bordercolor="white", borderwidth=2, borderpad=6
        )

        fig_bar.update_layout(
            paper_bgcolor='black', plot_bgcolor='black', font=dict(color="white"),
            xaxis=dict(showgrid=False, tickfont=dict(color="white")),
            yaxis=dict(visible=False, range=[0, max(val_25, val_bu, val_24) + 15]),
            height=500, margin=dict(t=50, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    if st.button("🔄 ACTUALIZAR DATOS"):
        st.rerun()
