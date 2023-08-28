import streamlit as st
from PIL import Image

im = Image.open("alpha.png")

st.set_page_config(
    page_title="Calcifire Consulting - AlphaChat",
    page_icon=im,
    layout="wide"
)
st.write("# Welcome to Alpha Playground! 👋")

st.sidebar.success("Login and select the demo from above.")

st.markdown(
    """
    Alpha Playground is a live demo of our app framework built specifically for
    Intelligent Systems and Business Solutions.
    
    👈 Login and select the demo from the sidebar to see some examples
    of what Alpha can do!
    ### Want to learn more?
    - Check out [Calcifire Consulting](https://calcifireconsulting.com)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### To See more complex demos Like:
    
    - Voice Chat
    - Voice Commands
    - Agent TTS (Text to Speech)
    - Computer Vision
    
    contact us at info@calcifireconsulting.com
"""
)

