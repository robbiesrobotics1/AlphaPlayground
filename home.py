import streamlit as st

st.set_page_config(
    page_title="Calcifire Consulting - Alpha Playground",
    page_icon="😎",
)

st.write("# Welcome to Alpha Playground! 👋")

st.sidebar.success("Select from one of the demos above.")

st.markdown(
    """
    Alpha Playground is a live demo of our app framework built specifically for
    Intelligent Systems and Business Solutions.
    
    **👈 Select a demo from the sidebar** to see some examples
    of what Alpha can do!
    ### Want to learn more?
    - Check out [Calcifire Consulting](https://calcifireconsulting.com)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### To See more complex demos Like:
    
    - Voice Chat Feature
    - Voice Commands
    - Agent TTS (Text to Speech)
    
    contact us at info@calcifireconsulting.com
"""
)

