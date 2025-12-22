import streamlit as st

# Configuración de la página
st.set_page_config(page_title="NPS Performance", layout="centered")

# 1. Cargar la imagen base (logo3.png)
# Usamos columnas para centrar la imagen si es necesario
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
with col_logo_2:
    st.image("logo3.png", use_container_width=True)

# 2. Título principal
st.markdown("<h1 style='text-align: center;'>NET PROMOTER SCORE PERFORMANCE</h1>", unsafe_allow_html=True)

# Añadimos un espacio en blanco para separar el título de los botones
st.write("\n" * 5)

# 3. Botones en la parte inferior
# Creamos dos columnas para que los botones estén uno al lado del otro
col1, col2 = st.columns(2)

with col1:
    if st.button("MONTHLY EVOLUTION", use_container_width=True):
        st.info("Cargando evolución mensual...")
        # Aquí iría la lógica para mostrar gráficos mensuales

with col2:
    if st.button("CURRENT MONTH", use_container_width=True):
        st.success("Mostrando datos del mes actual")
        # Aquí iría la lógica para mostrar el KPI del mes
