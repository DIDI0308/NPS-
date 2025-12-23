import streamlit as st
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Monthly Evolution NPS", layout="wide")

# --- DATOS EXTRAÍDOS ---
meses = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

# Datos NPS
ytd_2025 = [47, 56, 57, 58, 54, 59, 59, 60, 65, 61, 65, 64]
ytd_bu = [54] * 12  # Representa el BGT (Budget) constante en 54
ytd_2024 = [40, 32, 50, 57, 45, 46, 47, 49, 53, 49, 45, 55]

# --- CREACIÓN DE LA GRÁFICA ---
fig = go.Figure()

# 1. Línea YTD 2025 (Azul - con parte punteada para proyecciones/actual)
# Nota: Plotly dibuja líneas continuas, para el efecto punteado de la imagen:
fig.add_trace(go.Scatter(
    x=meses, y=ytd_2025,
    mode='lines+markers+text',
    name='YTD 2025',
    line=dict(color='#005587', width=3),
    text=ytd_2025,
    textposition="top center",
    textfont=dict(color="white")
))

# 2. Línea BGT (Verde - Constante)
fig.add_trace(go.Scatter(
    x=meses, y=ytd_bu,
    mode='lines+text',
    name='BGT',
    line=dict(color='#006A4D', width=3),
    text=[54 if m == "ENE" else "" for m in meses], # Etiqueta solo al inicio para limpieza
    textposition="middle left",
    textfont=dict(color="white")
))

# 3. Línea YTD 2024 (Naranja)
fig.add_trace(go.Scatter(
    x=meses, y=ytd_2024,
    mode='lines+markers+text',
    name='YTD 2024',
    line=dict(color='#E87722', width=3),
    text=ytd_2024,
    textposition="bottom center",
    textfont=dict(color="white")
))

# --- DISEÑO DEL LAYOUT (Fondo Negro) ---
fig.update_layout(
    title=dict(
        text="NPS",
        x=0.5,
        font=dict(color="white", size=24)
    ),
    paper_bgcolor='black',
    plot_bgcolor='black',
    xaxis=dict(
        showgrid=False,
        tickfont=dict(color="white"),
        linecolor='white',
        mirror=True
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#333333',
        tickfont=dict(color="white"),
        range=[min(ytd_2024)-5, max(ytd_2025)+10],
        showticklabels=False # En tu imagen no se ven los números del eje Y
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(color="white")
    ),
    margin=dict(l=20, r=20, t=100, b=20),
    height=500
)

# --- MOSTRAR EN STREAMLIT ---
st.title("Monthly Evolution Performance")
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos inferior (Opcional, para imitar el formato de la imagen)
st.write("### Resumen de Datos")
data_resumen = {
    "Métrica": ["YTD 2025", "BGT", "YTD 2024"],
    **{m: [y25, b, y24] for m, y25, b, y24 in zip(meses, ytd_2025, ytd_bu, ytd_2024)}
}
st.table(data_resumen)
