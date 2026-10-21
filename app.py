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
st.write("Habla por el micrófono: se transcribirá, se traducirá y se reproducirá en audio en tiempo real.")

col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma que hablas:", ["es-ES", "en-US", "fr-FR", "de-DE"], index=0)
with col2:
    idioma_destino = st.selectbox("Idioma a traducir:", ["en", "es", "fr", "de"], index=0)

lang_code_src = idioma_origen.split("-")[0]

st.write("---")
st.subheader("📝 Resultados y Audio")

caja_texto_original = st.empty()
caja_texto_traducido = st.empty()
caja_audio_reproductor = st.empty()

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
            
            # Acumula aprox. 2 segundos de audio para procesarlo
            if len(self.audio_buffer) > 16000 * 4:
                audio_data = sr.AudioData(bytes(self.audio_buffer), frame.sample_rate, 2)
                self.audio_buffer.clear()
                
                try:
                    # Transcripción
                    texto = self.recognizer.recognize_google(audio_data, language=idioma_origen)
                    if texto:
                        # Traducción
                        traduccion = GoogleTranslator(source=lang_code_src, target=idioma_destino).translate(texto)
                        
                        # Mostrar texto en pantalla
                        caja_texto_original.success(f"**Texto detectado ({idioma_origen}):** {texto}")
                        caja_texto_traducido.info(f"**Traducción ({idioma_destino}):** {traduccion}")
                        
                        # Generar audio de la traducción (gTTS)
                        tts = gTTS(text=traduccion, lang=idioma_destino)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        
                        # Reproducir audio automáticamente en la interfaz
                        with caja_audio_reproductor.container():
                            st.audio(fp, format="audio/mp3", autoplay=True)
                            
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

if webrtc_ctx.state.playing:
    st.success("🔴 Conectado: Habla por el micrófono para traducir en vivo...")
else:
    caja_texto_original.info("ℹ️ Haz clic en **Start** para activar el micrófono.")