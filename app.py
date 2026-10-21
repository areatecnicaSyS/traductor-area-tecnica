import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

st.set_page_config(page_title="Traductor en Vivo y Seguro", page_icon="🎙️")

# --- SISTEMA DE CONTRASEÑA PARA SEGURIDAD ---
def verificar_password():
    if "password_correcta" not in st.session_state:
        st.session_state["password_correcta"] = False

    if st.session_state["password_correcta"]:
        return True

    st.title("🔒 Acceso Restringido")
    st.write("Ingresa la contraseña para acceder al traductor en vivo.")
    
    password_ingresada = st.text_input("Contraseña:", type="password")
    
    if st.button("Ingresar"):
        # Cambia 'TuPasswordSeguro123' por la contraseña que desees compartir con la otra persona
        if password_ingresada == "TuPasswordSeguro123":
            st.session_state["password_correcta"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    return False

if not verificar_password():
    st.stop()

# --- APLICACIÓN EN VIVO ---
st.title("🎙️ Traductor de Voz en Vivo")
st.write("Habla por el micrófono y transmite en tiempo real con la persona al otro lado del enlace.")

# Configuración de idiomas
col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma que hablas:", ["es-ES", "en-US", "fr-FR", "de-DE"], index=0)
with col2:
    idioma_destino = st.selectbox("Idioma a traducir:", ["en", "es", "fr", "de"], index=0)

lang_code_src = idioma_origen.split("-")[0]

st.write("---")
st.subheader("🔴 Transmisión de Audio en Directo")

# Canal de WebRTC para streaming de voz en tiempo real
webrtc_ctx = webrtc_streamer(
    key="traductor-voz-en-vivo",
    mode=WebRtcMode.SENDONLY,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": False, "audio": True},
)

if webrtc_ctx.state.playing:
    st.success("🟢 Conectado y escuchando en vivo... Habla con normalidad.")
else:
    st.info("ℹ️ Haz clic en **Start** para activar el micrófono y comenzar la transmisión en vivo.")