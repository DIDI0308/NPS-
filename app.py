# --- 3. SECCIÓN DE GRÁFICAS GLOBALES (FILA 1) ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📊 Resumen Global")

# Creamos dos columnas para que las gráficas queden una al lado de la otra
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("### 1. Primary Driver Composition")
    data_anillo = df.groupby('Primary Driver')['Customer ID'].count().reset_index()
    fig_pie = px.pie(
        data_anillo, 
        values='Customer ID', 
        names='Primary Driver',
        hole=0.6,
        color_discrete_sequence=['#FFFF00', '#FFD700', '#FFEA00', '#FDDA0D'],
        template="plotly_dark"
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        legend_font_color="white",
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_graf2:
    st.markdown("### 2. Average Score Per Primary Driver")
    # Preparación de datos (Igual a tu lógica de limpieza)
    data_lineas_global = df.groupby('Primary Driver')['Score'].mean().sort_values(ascending=False).reset_index()
    
    # Crear gráfica de líneas en Plotly
    fig_lineas = px.line(
        data_lineas_global, 
        x='Primary Driver', 
        y='Score', 
        text=data_lineas_global['Score'].apply(lambda x: f'{x:.2f}'),
        markers=True,
        template="plotly_dark"
    )
    
    # Personalización para que coincida con tus colores
    fig_lineas.update_traces(
        line_color='#FFD700', 
        line_width=3,
        marker=dict(size=12, color='#FFD700'),
        textposition="top center",
        textfont=dict(color="white", size=14)
    )
    
    fig_lineas.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[6, 10], gridcolor='#333333'),
        xaxis=dict(tickangle=45),
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    st.plotly_chart(fig_lineas, use_container_width=True)
