# ==========================================
# VISTA 4: EA / LP (SOLUCIÓN DEFINITIVA)
# ==========================================
elif st.session_state.page == "ea_lp":
    # 1. Función con bypass de caché total
    def get_data_absolute_new():
        try:
            u = "https://docs.google.com/spreadsheets/d/1Xxm55SMKuWPMt9EDji0-ccotPzZzLcdj623wqYcwlBs/edit?usp=sharing".split('/edit')[0]
            csv_url = f"{u}/export?format=csv&nocache={pd.Timestamp.now().timestamp()}"
            res = requests.get(csv_url)
            return pd.read_csv(StringIO(res.text))
        except: return pd.DataFrame()

    # 2. Inyección de CSS
    st.markdown("""
        <style>
        .stApp { background-color: #000000 !important; }
        div.stButton > button {
            background-color: #FFFF00 !important;
            color: black !important;
            font-weight: bold !important;
            border: 2px solid #FFFF00 !important;
        }
        .banner-ea-lp {
            background-color: #FFFF00;
            padding: 8px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

    c_nav1, c_nav2 = st.columns([8, 2])
    with c_nav1:
        if st.button("⬅ VOLVER", key="btn_v_home"):
            st.session_state.page = "home"; st.rerun()
    with c_nav2:
        if st.button("🔄 ACTUALIZAR", key="btn_v_refresh"):
            st.cache_data.clear(); st.rerun()

    st.markdown('<div class="banner-ea-lp"><h2 style="color:black; margin:0; font-family:Arial Black; font-size:22px;">PERFORMANCE EA / LP</h2></div>', unsafe_allow_html=True)

    df_raw = get_data_absolute_new()

    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.strip()
        df_raw['Primary Driver'] = df_raw['Primary Driver'].astype(str).str.strip().str.upper()
        df_delivery = df_raw[df_raw['Primary Driver'] == 'DELIVERY'].copy()

        def clean_reg(x):
            x = str(x).upper()
            if 'ALTO' in x or 'EA' in x: return 'EA'
            if 'PAZ' in x or 'LP' in x: return 'LP'
            return 'OTRO'
        
        df_delivery['REG_GROUP'] = df_delivery['Sales Region'].apply(clean_reg)
        df_final = df_delivery[df_delivery['REG_GROUP'].isin(['EA', 'LP'])].copy()

        if not df_final.empty:
            df_plot = df_final.groupby(['Category', 'REG_GROUP'])['Customer ID'].count().reset_index()
            df_plot['Total_Barra'] = df_plot.groupby('Category')['Customer ID'].transform('sum')
            df_plot['Altura'] = (df_plot['Customer ID'] / df_plot['Total_Barra']) * 100

            col_izq, col_der = st.columns([1.5, 2.5])
            
            with col_izq:
                st.markdown('<p style="color:#FFFF00; font-size:16px; font-weight:bold; text-align:center;">DISTRIBUCIÓN DE CLIENTES</p>', unsafe_allow_html=True)
                fig = px.bar(
                    df_plot, 
                    x="Category", 
                    y="Altura", 
                    color="REG_GROUP", 
                    text="Customer ID",
                    color_discrete_map={'EA': '#FFFF00', 'LP': '#DAA520'},
                    category_orders={"Category": ["Detractor", "Passive", "Promoter"]},
                    barmode="stack"
                )
                fig.update_layout(
                    paper_bgcolor='black', plot_bgcolor='black',
                    height=380, yaxis=dict(showticklabels=False, showgrid=False, title=None),
                    xaxis=dict(title=None, tickfont=dict(color="white", size=11), showgrid=False),
                    legend=dict(title=None, font=dict(color="white"), orientation="h", y=1.1, x=0.5, xanchor="center"),
                    margin=dict(t=5, b=5, l=5, r=5)
                )
                st.plotly_chart(fig, use_container_width=True, key=f"force_chart_{pd.Timestamp.now().microsecond}")
            
            with col_der:
                # --- GRÁFICA DE BARRAS HORIZONTALES APILADAS ---
                # Agrupamos por Secondary Driver y Región para la gráfica horizontal
                df_horiz_data = df_final.groupby(['Secondary Driver', 'REG_GROUP'])['Customer ID'].count().reset_index()
                
                fig_horiz = px.bar(
                    df_horiz_data,
                    y="Secondary Driver",
                    x="Customer ID",
                    color="REG_GROUP",
                    orientation='h',
                    text="Customer ID",
                    color_discrete_map={'EA': '#FFFF00', 'LP': '#CC9900'},
                    template="plotly_dark"
                )
                fig_horiz.update_layout(
                    paper_bgcolor='black', plot_bgcolor='black',
                    height=500,
                    xaxis=dict(title="Número de Clientes", showgrid=False, tickfont=dict(color="white")),
                    yaxis=dict(title=None, tickfont=dict(color="white", size=12)),
                    legend=dict(title=None, font=dict(color="white"), orientation="h", y=1.1, x=0.5, xanchor="center"),
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                fig_horiz.update_traces(textposition='inside', textfont=dict(color="black", size=14))
                st.plotly_chart(fig_horiz, use_container_width=True, key=f"horiz_bar_v4_{pd.Timestamp.now().microsecond}")
        else:
            st.warning("No hay datos de Delivery.")
    else:
        st.error("Error de conexión con la base de datos.")
