import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import av
import threading
import io

st.set_page_config(page_title="Traductor Total en Vivo", page_icon="🎙️")

# --- 1. SISTEMA DE CONTRASEÑA ---
PASSWORD_DEFECTO = "MiClaveSecreta123"

def verificar_password():
    if "password_correcta" not in st.session_state:
        st.session_state["password_correcta"] = False

    if st.session_state["password_correcta"]:
        return True

    st.title("🔒 Acceso Restringido")
    st.write("Ingresa la contraseña autorizada para acceder al traductor en vivo.")
    
    password_ingresada = st.text_input("Contraseña:", type="password")
    
    if st.button("Ingresar"):
        password_real = st.secrets.get("PASSWORD_APP", PASSWORD_DEFECTO)
        if password_ingresada == password_real:
            st.session_state["password_correcta"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Inténtalo de nuevo.")
    return False

if not verificar_password():
    st.stop()

# --- 2. INTERFAZ PRINCIPAL ---
st.title("🎙️ Traductor Total de Voz en Vivo")
st.write("Habla por el micrófono: se transcribirá, se traducirá y aparecerá el reproductor de audio.")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma que hablas:", ["es-ES", "en-US", "fr-FR", "de-DE"], index=0)
with col2:
    idioma_destino = st.selectbox("Idioma a traducir:", ["en", "es", "fr", "de"], index=0)

lang_code_src = idioma_origen.split("-")[0]

st.write("---")
st.subheader("📝 Resultados y Audio")

# Contenedores para almacenar el estado en la sesión de Streamlit
if "texto_original" not in st.session_state:
    st.session_state["texto_original"] = "Esperando audio..."
if "texto_traducido" not in st.session_state:
    st.session_state["texto_traducido"] = "..."
if "audio_bytes" not in st.session_state:
    st.session_state["audio_bytes"] = None

caja_texto_original = st.empty()
caja_texto_traducido = st.empty()
caja_audio = st.empty()

# --- 3. PROCESADOR DE AUDIO EN TIEMPO REAL ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_buffer = bytearray()
        self.lock = threading.Lock()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        sound = frame.to_ndarray()
        with self.lock:
            self.audio_buffer.extend(sound.tobytes())
            
            # Acumula aprox. 2 segundos de audio
            if len(self.audio_buffer) > 16000 * 4:
                audio_data = sr.AudioData(bytes(self.audio_buffer), frame.sample_rate, 2)
                self.audio_buffer.clear()
                
                try:
                    texto = self.recognizer.recognize_google(audio_data, language=idioma_origen)
                    if texto:
                        traduccion = GoogleTranslator(source=lang_code_src, target=idioma_destino).translate(texto)
                        
                        # Guardamos en session_state para actualizar la interfaz
                        st.session_state["texto_original"] = texto
                        st.session_state["texto_traducido"] = traduccion
                        
                        # Generar audio con gTTS
                        tts = gTTS(text=traduccion, lang=idioma_destino)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.session_state["audio_bytes"] = fp.getvalue()
                            
                except Exception:
                    pass
                    
        return frame

# --- 4. STREAMER DE WEBRTC ---
webrtc_ctx = webrtc_streamer(
    key="traductor-total-vivo",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": False, "audio": True},
)

# Mostrar resultados actualizados en pantalla
caja_texto_original.success(f"**Texto detectado:** {st.session_state['texto_original']}")
caja_texto_traducido.info(f"**Traducción:** {st.session_state['texto_traducido']}")

if st.session_state["audio_bytes"]:
    caja_audio.audio(st.session_state["audio_bytes"], format="audio/mp3")

if webrtc_ctx.state.playing:
    st.markdown("🔴 **Conectado:** Habla por el micrófono...")
else:
    st.info("ℹ️ Haz clic en **Start** para activar el micrófono.")