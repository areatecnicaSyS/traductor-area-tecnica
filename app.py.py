import streamlit as st
from deep_translator import GoogleTranslator

# Configuración de la página
st.set_page_config(
    page_title="Traductor Profesional - Área Técnica",
    page_icon="🌎",
    layout="centered"
)

st.title("🌎 Traductor de Texto Inteligente")
st.markdown("Herramienta desarrollada para *Área Técnica Servicios y Soluciones Tecnológicas*.")

# Diccionario de idiomas comunes
idiomas = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Portugués": "pt",
    "Italiano": "it",
    "Alemán": "de",
    "Chino Simplificado": "zh-CN"
}

# Interfaz de selección de idiomas
col1, col2 = st.columns(2)

with col1:
    idioma_origen_nombre = st.selectbox("Idioma de origen:", ["Detectar automáticamente"] + list(idiomas.keys()))

with col2:
    idioma_destino_nombre = st.selectbox("Idioma de destino:", list(idiomas.keys()), index=1)

# Área de texto para ingresar contenido
texto_a_traducir = st.text_area("Ingresa el texto que deseas traducir:", height=150)

# Botón de traducción
if st.button("Traducir Texto", type="primary"):
    if not texto_a_traducir.strip():
        st.warning("Por favor, ingresa algún texto para traducir.")
    else:
        try:
            # Configurar el traductor
            target_code = idiomas[idioma_destino_nombre]
            
            if idioma_origen_nombre == "Detectar automáticamente":
                translator = GoogleTranslator(source='auto', target=target_code)
            else:
                source_code = idiomas[idioma_origen_nombre]
                translator = GoogleTranslator(source=source_code, target=target_code)
            
            # Realizar la traducción
            traduccion = translator.translate(texto_a_traducir)
            
            # Mostrar resultado
            st.success("¡Traducción completada!")
            st.markdown("### Resultado:")
            st.info(traduccion)
            
            # Botón para descargar el resultado
            st.download_button(
                label="Descargar traducción en TXT",
                data=traduccion,
                file_name="traduccion_area_tecnica.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"Ocurrió un error al realizar la traducción: {e}")