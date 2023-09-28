from alphaagent import query_agent, create_agent, write_response, decode_response
import pandas as pd
import streamlit as st
import tabula
from PIL import Image
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report
import pygwalker as pyg
import streamlit.components.v1 as components
import streamlit_authenticator as stauth
import database as db

############ Set up page configuration and favicon ################
basewidth = 600
favicon = Image.open("static/alpha.png")
wpercent = (basewidth / float(favicon.size[0]))
hsize = int((float(favicon.size[1]) * float(wpercent)))
img = favicon.resize((basewidth, hsize), Image.LANCZOS)
img.save('static/resized_image.png')
st.set_page_config(
    page_title="Alpha-Graph",
    page_icon= img,
    layout="wide",
    initial_sidebar_state="expanded")
####################################################################


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
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password') 
#####################################################################



################# Initialize Session States #######################################
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-0613"
if "tab2_content" not in st.session_state:
    st.session_state.tab2_content = []
if "tab3_content" not in st.session_state:
    st.session_state.tab3_content = []
if "tab4_content" not in st.session_state:
    st.session_state.tab4_content = [] 
###################################################################################
if authentication_status:

    data = st.sidebar.file_uploader("Upload a File")
    ChatBot = st.container()
    with ChatBot:
        st.title("Visualize Data With Alpha")
        st.text("Intelligent chatbot with access to your documents. \nUpload a file to get insights")
        tab2, tab3, tab4 = st.tabs(["PDF Convert", "Data Profiler", "Insights Builder"])  
####################################################################


####################### PDF Convert TO CSV #############################                   
    with tab2:
        file = data
        converted_file = (r"static/test.csv")
        
        if st.sidebar.button("Convert PDF"):
            df = tabula.read_pdf(input_path = file, pages = "all")
            tabula.convert_into(input_path = file, output_path = converted_file, output_format = "csv", pages = "all", stream = True)
            st.write("Tabulated Data:")
            st.chat_message("ai").write(df)                          
                   
                    
    ####################### Tab 3 - Data Profiler #######################################        
    with tab3:
        st.title("Data Profiler")
        if st.sidebar.button("Profile Data"):
            df = pd.read_csv(data)
            pr = df.profile_report()
            #st_profile_report(pr)

            # Append the generated report to the Session State as "tab3_content"
            if "tab3_content" not in st.session_state:
                st.session_state.tab3_content = []

            # Store the report in Session State
            st.session_state.tab3_content.append(pr)

        # Display the content from Session State
        st.text("Profiling Data:")
        if st.session_state.tab3_content:
            for content in st.session_state.tab3_content:
                st_profile_report(content)
                            
    ####################### Tab 4 - Insights Builder (Advanced DataViz) ###################          
        
    with tab4:
        st.title("Insights Builder")
        if st.sidebar.button("Build Insights"):
            df = pd.read_csv(data)
            pyg_html = pyg.walk(df, return_html=True)
            #components.html(pyg_html, height=1000, scrolling=True)

            # Append the generated output to the Session State as "tab4_content"
            if "tab4_content" not in st.session_state:
                st.session_state.tab4_content = []

            # Store the generated output in Session State
            st.session_state.tab4_content.append(pyg_html)

        # Display the content from Session State
        st.text("Insights:")
        if st.session_state.tab4_content:
            for content in st.session_state.tab4_content:
                components.html(content, height=1000, scrolling=True)

    authenticator.logout('Logout', 'sidebar',) 
    st.sidebar.write("[Terms of Service](https://docs.google.com/document/d/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)") 
    st.sidebar.write("[Privacy Policy](https://docs.google.com/document/d/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)") 
else:
        st.write("# Welcome to Alpha Playground! 👋")

        #st.sidebar.success("Login and select the demo from above.")
        st.chat_message("ai").write("Hi. I'm Alpha, your friendly intelligent assistant. To get started, enter your username and password in the left sidebar.")
        
        st.markdown(
            """
            Alpha Playground is a live demo of our app framework built specifically for
            Intelligent Systems and Business Solutions.
            
            👈 Login to see some examples
            of what Alpha can do!
            ### Want to learn more?
            - Check out [Calcifire Consulting](https://calcifireconsulting.com)
            - Jump into our [documentation](https://docs.streamlit.io)
            - Ask a question in our [community
                forums](https://discuss.streamlit.io)
            ### To See more complex demos Like:
            
            - Voice Chat (Speech to Text)
            - Voice Commands (Keyword Implementation)
            - Agent TTS (Text to Speech)
            - Computer Vision
            
            contact us at info@calcifireconsulting.com
        """
        )    
            