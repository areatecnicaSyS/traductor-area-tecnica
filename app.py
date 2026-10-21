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
st.write("Selecciona los idiomas, graba tu voz y la aplicación traducirá y hablará en el idioma de destino.")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma que hablas:", ["Español (es-ES)", "Inglés (en-US)", "Francés (fr-FR)"], index=0)
with col2:
    idioma_destino = st.selectbox("Idioma de traducción:", ["Inglés (en)", "Español (es)", "Francés (fr)", "Alemán (de)"], index=0)

# Extraer códigos correctos para el traductor
lang_map = {
    "Español (es-ES)": "es",
    "Inglés (en-US)": "en",
    "Francés (fr-FR)": "fr",
    "Inglés (en)": "en",
    "Español (es)": "es",
    "Francés (fr)": "fr",
    "Alemán (de)": "de"
}

lang_code_src = lang_map[idioma_origen]
lang_code_dst = lang_map[idioma_destino]
speech_lang_src = "es-ES" if "es" in lang_code_src else ("en-US" if "en" in lang_code_src else "fr-FR")

st.write("---")

# Grabador de audio nativo de Streamlit (compatible con celulares y PC bajo HTTPS)
audio_bytes = st.audio_input("Graba tu voz:")

if audio_bytes is not None:
    st.info("🔄 Procesando y traduciendo...")
    
    try:
        recognizer = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes.read())
        
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            
            # Reconocer voz según el idioma que hablas
            texto = recognizer.recognize_google(audio_data, language=speech_lang_src)
            
            if texto:
                # Traducir al idioma de destino seleccionado
                traduccion = GoogleTranslator(source=lang_code_src, target=lang_code_dst).translate(texto)
                
                # Mostrar resultados
                st.success(f"**Lo que dijiste ({idioma_origen}):** {texto}")
                st.info(f"**Traducción ({idioma_destino}):** {traduccion}")
                
                # Generar y reproducir audio traducido
                tts = gTTS(text=traduccion, lang=lang_code_dst)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                st.audio(fp, format="audio/mp3", autoplay=True)
                
    except sr.UnknownValueError:
        st.warning("No se pudo entender el audio. Habla claro y cerca del micrófono.")
    except Exception as e:
        st.error(f"Error al procesar: {e}")