import pygwalker as pyg
import pandas as pd
import streamlit.components.v1 as components
import streamlit as st


# Adjust the width of the Streamlit page
st.set_page_config(
 
    layout="wide"
)

# Add Title
st.title("Alpha - Data Exploration & Vizualization")
csv_file= st.file_uploader("Upload Your CSV")

if st.button("Explore Data"):
    # Import your data
    
    df = pd.read_csv(csv_file)
 
    # Generate the HTML using Pygwalker
    pyg_html = pyg.walk(df, return_html=True)
 
    # Embed the HTML into the Streamlit app
    components.html(pyg_html, height=1000, scrolling=True)