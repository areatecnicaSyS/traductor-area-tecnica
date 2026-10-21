import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

st.set_page_config(page_title="Traductor en Vivo", page_icon="🎙️")

# --- 1. SISTEMA DE CONTRASEÑA ---
PASSWORD_DEFECTO = "MiClaveSecreta123"

def verificar_password():
    if "password_correcta" not in st.session_state:
        st.session_state["password_correcta"] = False

    if st.session_state["password_correcta"]:
        return True

    st.title("🔒 Acceso Restringido")
    st.write("Ingresa la contraseña autorizada para acceder al traductor.")
    
    password_ingresada = st.text_input("Contraseña:", type="password")
    
    if st.button("Ingresar"):
        password_real = st.secrets.get("PASSWORD_APP", PASSWORD_DEFECTO)
        if password_ingresada == password_real:
            st.session_state["password_correcta"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    return False

if not verificar_password():
    st.stop()

# --- 2. INTERFAZ PRINCIPAL ---
st.title("🎙️ Traductor en Vivo")
st.write("Usa el grabador de audio integrado para hablar: se traducirá y reproducirá al instante.")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma origen:", ["es-ES", "en-US", "fr-FR", "de-DE"], index=0)
with col2:
    idioma_destino = st.selectbox("Traducir a:", ["en", "es", "fr", "de"], index=0)

lang_code_src = idioma_origen.split("-")[0]

st.write("---")

# Componente nativo de Streamlit para interactuar con el micrófono del celular/PC de forma segura
audio_bytes = st.audio_input("Graba tu voz para traducir en vivo:")

if audio_bytes is not None:
    st.info("🔄 Procesando y traduciendo audio...")
    
    try:
        recognizer = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes.read())
        
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            
            # Reconocer voz
            texto = recognizer.recognize_google(audio_data, language=idioma_origen)
            
            if texto:
                # Traducir texto
                traduccion = GoogleTranslator(source=lang_code_src, target=idioma_destino).translate(texto)
                
                # Mostrar resultados
                st.success(f"**Texto detectado:** {texto}")
                st.info(f"**Traducción:** {traduccion}")
                
                # Generar y reproducir audio traducido
                tts = gTTS(text=traduccion, lang=idioma_destino)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                st.audio(fp, format="audio/mp3", autoplay=True)
                
    except sr.UnknownValueError:
        st.warning("No se pudo entender el audio. Intenta hablar un poco más cerca del micrófono.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el audio: {e}")