import cv2
import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import numpy as np
from play import RamperVirtualPainter

st.set_page_config(page_title="FunDraw_ChemLab", layout="wide")

import queue

# CSS for modern dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 50px;
        font-weight: 600;
        background-color: #262730;
        color: white;
        border: 1px solid #404040;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #404040;
        border-color: #00aaff;
        color: #00aaff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    /* Specific button styling based on label content (hacky but works for pure streamlit) */
    
    /* Headers */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00aaff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 FunDraw_ChemLab")

if "command_queue" not in st.session_state:
    st.session_state["command_queue"] = queue.Queue()

# RTC Configuration for Cloud (Render)
# RTC Configuration
import os
from twilio.rest import Client

# Default STUN servers
ice_servers = [
    {"urls": ["stun:stun.l.google.com:19302"]},
    {"urls": ["stun:stun1.l.google.com:19302"]},
    {"urls": ["stun:stun2.l.google.com:19302"]},
]

# If Twilio credentials are provided, fetch TURN servers
# This is crucial for cloud deployment where STUN is not enough
if "TWILIO_ACCOUNT_SID" in os.environ and "TWILIO_AUTH_TOKEN" in os.environ:
    try:
        client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        token = client.tokens.create()
        ice_servers = token.ice_servers
    except Exception as e:
        print(f"Error fetching Twilio TURN servers: {e}")

RTC_CONFIGURATION = RTCConfiguration({"iceServers": ice_servers})

class VideoProcessor:
    def __init__(self, command_queue):
        self.command_queue = command_queue
        self.painter = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        
        if self.painter is None:
            self.painter = RamperVirtualPainter(
                width=img.shape[1], 
                height=img.shape[0], 
                command_queue=self.command_queue
            )

        try:
            processed_img = self.painter.process_frame(img)
        except Exception as e:
            # print(f"Error processing frame: {e}")
            processed_img = img

        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

# Factory to pass the queue to the processor
import functools

def main():
    col1, col2 = st.columns([3, 1])

    with col1:
        # Create the queue if it doesn't exist
        if "command_queue" not in st.session_state:
            st.session_state["command_queue"] = queue.Queue()
            
        # Capture the queue object in a local variable to pass to the thread safely
        cmd_queue = st.session_state["command_queue"]
            
        # factory wrapper uses the captured variable
        def video_processor_factory():
            return VideoProcessor(cmd_queue)

        webrtc_streamer(
            key="ramper-painter",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=video_processor_factory,
            media_stream_constraints={
                "video": {"width": {"ideal": 1280}, "height": {"ideal": 720}},
                "audio": False
            },
            async_processing=True,
        )

    with col2:
        st.markdown("### Controls")
        
        if st.button("🧪 Chemistry Lab", help="Switch to Chemistry Mode"):
            st.session_state["command_queue"].put({"type": "mode", "value": "CHEMISTRY"})
            
        if st.button("🎨 Painter Mode", help="Switch to Painter Mode"):
            st.session_state["command_queue"].put({"type": "mode", "value": "PAINTER"})

        st.markdown("---")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("➖"):
                st.session_state["command_queue"].put({"type": "brush_size", "action": "decrease"})
        with c2:
            st.markdown("<div style='text-align: center; line-height: 50px; font-weight: bold;'>Brush Size</div>", unsafe_allow_html=True)
        with c3:
            if st.button("➕"):
                st.session_state["command_queue"].put({"type": "brush_size", "action": "increase"})

        st.markdown("---")
        
        if st.button("🗑️ Clear Canvas"):
            st.session_state["command_queue"].put({"type": "clear"})
            
        if st.button("💾 Save Art"):
            st.session_state["command_queue"].put({"type": "save"})
            st.success("Saved to disk!")

    st.markdown("---")
    st.markdown("Built with OpenCV, MediaPipe, and Streamlit.")

if __name__ == "__main__":
    main()
