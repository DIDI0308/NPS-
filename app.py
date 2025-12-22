import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap

def render_dashboard(df, mes_base):
    # Banner Superior
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL INICIO"):
        st.session_state.page = 'landing'
        st.rerun()

    # (Aquí iría la lógica de logos que ya tienes en el original)
    st.markdown(f'<div class="banner-amarillo"><div class="titulo-texto"><h1>NPS 2025</h1><h2>{mes_base}</h2></div></div>', unsafe_allow_html=True)

    if not df.empty:
        # Fila 1: Composición y Score Promedio
        col_g1, col_g2 = st.columns(2)
        df_global = df[df['Primary Driver'] != 'N/A'].copy()

        with col_g1:
            st.markdown('<p style="font-size:22px; font-weight:bold; margin-left:20px;">1. Primary Driver Composition</p>', unsafe_allow_html=True)
            data_anillo = df_global.groupby('Primary Driver')['Customer ID'].count().reset_index()
            fig1 = px.pie(data_anillo, values='Customer ID', names='Primary Driver', hole=0.6, color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00'])
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.markdown('<p style="font-size:22px; font-weight:bold;">2. Average Score Per Primary Driver</p>', unsafe_allow_html=True)
            data_lineas = df_global.groupby('Primary Driver')['Score'].mean().reset_index().sort_values(by='Score', ascending=False)
            fig2 = px.line(data_lineas, x='Primary Driver', y='Score', markers=True)
            fig2.update_traces(line_color='#FFD700', marker=dict(size=10, color='#FFD700'), text=data_lineas['Score'].map('{:.2f}'.format), textposition="top center", mode='lines+markers+text')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig2, use_container_width=True)

        # Filtros y Gráficas Secundarias
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        c_f1, c_f2 = st.columns(2)
        selector_driver = c_f1.selectbox('Primary Driver:', ['All'] + sorted([d for d in df['Primary Driver'].unique() if d != 'N/A']))
        opciones_cat = sorted([cat for cat in df['Category'].unique() if cat != 'N/A'])
        selector_cat = c_f2.multiselect('Category:', opciones_cat, default=opciones_cat)

        # ... (Resto de la lógica de filtrado, barras horizontales y comentarios)
