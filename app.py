import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator, MyMemoryTranslator
from gtts import gTTS
from pydub import AudioSegment
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

# --- FUNCIÓN DE TRADUCCIÓN A PRUEBA DE BLOQUEOS ---
def traducir_texto(texto, src, dst):
    """
    Intenta traducir usando GoogleTranslator. Si alcanza el límite de peticiones,
    usa automáticamente MyMemoryTranslator como respaldo.
    """
    try:
        return GoogleTranslator(source=src, target=dst).translate(texto)
    except Exception:
        # Respaldo rápido y gratuito cuando Google bloquea la IP
        return MyMemoryTranslator(source=src, target=dst).translate(texto)

# --- 2. INTERFAZ PRINCIPAL ---
st.title("🎙️ Traductor en Vivo")
st.write("Selecciona los idiomas, graba tu voz y la aplicación traducirá al instante.")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma que hablas:", ["Español (es-ES)", "Inglés (en-US)", "Francés (fr-FR)"], index=0)
with col2:
    idioma_destino = st.selectbox("Idioma de traducción:", ["Inglés (en)", "Español (es)", "Francés (fr)", "Alemán (de)"], index=0)

# Mapeo seguro de idiomas
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

# Componente de audio de Streamlit
audio_bytes = st.audio_input("Graba tu frase (habla claro y sin pausas largas):")

if audio_bytes is not None:
    st.info("🔄 Procesando tu voz...")
    
    try:
        # Convertir WebM/OGG a WAV PCM en memoria
        audio_bytes_data = audio_bytes.read()
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes_data))
        
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # Reconocimiento de voz
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_io) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = recognizer.record(source)
            
            texto = recognizer.recognize_google(audio_data, language=speech_lang_src)
            
            if texto and texto.strip():
                # Traducción segura
                traduccion = traducir_texto(texto, lang_code_src, lang_code_dst)
                
                # Mostrar resultados
                st.success(f"**Lo que dijiste:** {texto}")
                st.info(f"**Traducción:** {traduccion}")
                
                # Reproducir audio traducido
                tts = gTTS(text=traduccion, lang=lang_code_dst)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                
                st.audio(fp, format="audio/mp3", autoplay=True)
            else:
                st.warning("El audio se grabó vacío o no se detectaron palabras.")
                
    except sr.UnknownValueError:
        st.warning("⚠️ No se pudo entender el audio. Habla más cerca del micrófono e inténtalo de nuevo.")
    except sr.RequestError:
        st.error("⚠️ Error de conexión con el servicio de voz. Inténtalo de nuevo.")
    except Exception as e:
        st.error(f"⚠️ Error al procesar: {e}")