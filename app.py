with col_d1:
    # --- DINÁMICA A: CATEGORY COMPOSITION (Stacked Bar) ---
    df_visual_cat = df_filt[df_filt['Category'] != 'N/A']
    conteo_cat = df_visual_cat['Category'].value_counts(normalize=True) * 100
    
    orden = ['Detractor', 'Passive', 'Promoter']
    color_map = {'Detractor': '#E74C3C', 'Passive': '#BDC3C7', 'Promoter': '#F1C40F'}
    
    fig_stack = go.Figure()
    for cat in orden:
        val = conteo_cat.get(cat, 0)
        fig_stack.add_trace(go.Bar(
            name=cat, 
            x=['Composition %'], 
            y=[val],
            marker_color=color_map[cat],
            text=f"{val:.1f}%" if val > 0 else "",
            textposition='auto',
            textfont=dict(color='black', size=14, family="Arial Black")
        ))

    # Título dinámico según selección
    titulo_dinamico = f"Category Composition: {selector_driver}" if selector_driver != 'All' else "Global Category Composition"

    fig_stack.update_layout(
        title={
            'text': titulo_dinamico,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': 'white'}
        },
        barmode='stack', 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"), 
        height=500, # Aumentamos altura para dar aire a la leyenda
        showlegend=True,
        # Ajuste fino de la leyenda para que no choque con el eje X
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.2, 
            xanchor="center", 
            x=0.5,
            font=dict(size=12)
        ),
        yaxis=dict(range=[0, 100], visible=False),
        xaxis=dict(tickfont=dict(size=14), color="white"),
        margin=dict(t=80, b=100, l=40, r=40) # Margen inferior amplio (b=100) para evitar sobreposición
    )
    
    st.plotly_chart(fig_stack, use_container_width=True)
