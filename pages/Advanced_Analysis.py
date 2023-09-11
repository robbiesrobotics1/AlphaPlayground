import json
import logging
import os
import subprocess
import sys
import time
from PIL import Image
import database as db
import streamlit_authenticator as stauth
import traceback
import openai
import pandas as pd
import streamlit as st
from plotly.graph_objs import Figure
from pydantic import BaseModel
from streamlit_chat import message
from chat2plot import ResponseType, chat2plot
from chat2plot.chat2plot import Chat2Vega

sys.path.append("../../")

############ Set up page configuration and favicon ################
basewidth = 600
favicon = Image.open("static/alpha.png")
wpercent = (basewidth / float(favicon.size[0]))
hsize = int((float(favicon.size[1]) * float(wpercent)))
img = favicon.resize((basewidth, hsize), Image.LANCZOS)
img.save('static/resized_image.png')
st.set_page_config(
    page_title="Alpha-Advanced-Analysis",
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded")

#####################################################################


########### Setup api Keys ###################################
# Retrieve secrets
ZAPIER_CLIENT_SECRET = st.secrets["ZAPIER_CLIENT_SECRET"]
ZAPIER_CLIENT_ID = st.secrets["ZAPIER_CLIENT_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
###############################################################


############# USER Authentication Creation ###########################
users = db.fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "AlphaChat", "abcdef", cookie_expiry_days= 1 )
name, authentication_status, username = authenticator.login("Login", "sidebar")
######################################################################


############### Authentication Status Conditionals ################
if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password') 
#####################################################################


def initialize_logger():
    logger = logging.getLogger("root")
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    return True


if "logger" not in st.session_state:
    st.session_state["logger"] = initialize_logger()

api_key = openai.api_key = st.secrets["OPENAI_API_KEY"]
csv_file = st.sidebar.file_uploader("Step1: Upload CSV/XLSX/XLS File", type={"csv"})

if csv_file is not None:
    try:
        # Check if the uploaded file is a valid CSV file
        df = pd.read_csv(csv_file)
        # Process the file further
        st.write("Tabulated Data:")
        st.write(df.head())
    except Exception as e:
        # Handle the exception and provide user feedback
        st.error(f"An error occurred while processing the uploaded file: {e}")

    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []

    st.subheader(f'*{st.session_state["name"]}* Chat History:')

    def initialize_c2p():
        st.session_state["chat"] = chat2plot(
            df,
            st.session_state["chart_format"],
            verbose=True,
            description_strategy="head",
        )

    def reset_history():
        initialize_c2p()
        st.session_state["generated"] = []
        st.session_state["past"] = []

    with st.sidebar:
        chart_format = st.selectbox(
            "Chart format",
            ("simple", "vega"),
            key="chart_format",
            index=0,
            on_change=initialize_c2p,
        )

        st.button("Reset conversation history", on_click=reset_history)

    if "chat" not in st.session_state:
        initialize_c2p()

    c2p = st.session_state["chat"]

    chat_container = st.container()
    input_container = st.container()

    def submit():
        submit_text = st.session_state["input"]
        st.session_state["input"] = ""
        with st.spinner(text="Waiting for Alpha's response..."):
            try:
                if isinstance(c2p, Chat2Vega):
                    res = c2p(submit_text, config_only=True)
                else:
                    res = c2p(submit_text, config_only=False, show_plot=False)
            except Exception:
                res = traceback.format_exc()
        st.session_state.past.append(submit_text)
        st.session_state.generated.append(res)

    def get_text():
        input_text = st.chat_input(f'*{st.session_state["name"]}*''s Prompt', key="input", on_submit=submit)
        return input_text

    with input_container:
        user_input = get_text()

    if st.session_state["generated"]:
        with chat_container:
            for i in range(
                len(st.session_state["generated"])):  # range(len(st.session_state["generated"]) - 1, -1, -1):
                message(st.session_state["past"][i], is_user=True, avatar_style="avataaars", seed="24", key=str(i) + "_user")

                res = st.session_state["generated"][i]

                if isinstance(res, str):
                    # something went wrong
                    st.error(res.replace("\n", "\n\n"))
                elif res.response_type == ResponseType.SUCCESS:
                    message(res.explanation, is_user=False, avatar_style="avataaars-neutral", seed="Aneka114", key=str(i))

                    col1, col2 = st.columns([2, 1])

                    with col2:
                        config = res.config
                        if isinstance(config, BaseModel):
                            st.code(
                                config.json(indent=2, exclude_none=True),
                                language="json",
                            )
                        else:
                            st.code(json.dumps(config, indent=2), language="english")
                    with col1:
                        if isinstance(res.figure, Figure):
                            st.plotly_chart(res.figure, use_container_width=True)
                        else:
                            st.vega_lite_chart(df, res.config, use_container_width=True)
                else:
                    st.warning(
                        f"Failed to render chart. last message: {res.conversation_history[-1].content}",
                        icon="⚠️",
                    )
                    # message(res.conversation_history[-1].content, key=str(i))