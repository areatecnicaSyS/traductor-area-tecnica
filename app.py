import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import io

st.set_page_config(page_title="Traductor en Vivo", page_icon="🎙️")

st.title("🎙️ Traductor por Voz en Vivo")
st.write("Transmisión directa de voz y traducción automática.")

# Selección de idiomas
col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("Idioma origen:", ["es-ES", "en-US", "fr-FR", "de-DE"], index=0)
with col2:
    idioma_destino = st.selectbox("Traducir a:", ["en", "es", "fr", "de"], index=0)

lang_code_src = idioma_origen.split("-")[0]

st.write("---")
st.subheader("Transmitir audio en directo:")

# Componente WebRTC para transmisión directa
webrtc_ctx = webrtc_streamer(
    key="traductor-live",
    mode=WebRtcMode.SENDONLY,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": False, "audio": True},
)

if webrtc_ctx.state.playing:
    st.info("🔴 Transmitiendo y escuchando en vivo...")