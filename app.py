import streamlit as st
import pandas as pd
import requests
import io

# 1. TRANSFORMACIÓN DEL LINK
# Hemos cambiado 'Doc.aspx' por 'download=1' para que SharePoint entregue el archivo bruto
SHAREPOINT_LINK = "https://anheuserbuschinbev.sharepoint.com/sites/CDElAlto/_layouts/15/download.aspx?UniqueId=06a11deb7e714f01a2a1a8676a16f071"

@st.cache_data(ttl=300) # Se actualiza cada 5 minutos
def load_data_from_sharepoint(url):
    try:
        # Intentar descargar el archivo
        response = requests.get(url)
        # Si el sitio requiere login corporativo, este paso podría fallar sin un token
        response.raise_for_status()
        
        # Leer el contenido del Excel
        df = pd.read_excel(io.BytesIO(response.content))
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Nota: Si el archivo es privado, asegúrate de que el enlace tenga permisos de 'Cualquier persona con el link' o usa autenticación MSAL.")
        return pd.DataFrame()

# --- INTERFAZ ---
st.title("Conexión Corporativa SharePoint")

df = load_data_from_sharepoint(SHAREPOINT_LINK)

if not df.empty:
    st.success("¡Datos cargados correctamente desde SharePoint!")
    st.dataframe(df.head()) # Vista previa
    
    # AQUÍ PUEDES PEGAR TU CÓDIGO DE GRÁFICAS ANTERIOR
else:
    st.warning("No se pudieron extraer datos. Revisa los permisos del archivo en SharePoint.")
