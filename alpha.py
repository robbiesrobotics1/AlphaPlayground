############## Import Modules ############################################
import openai
import streamlit as st
import streamlit_chat
from PIL import Image
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report
import pygwalker as pyg
import pandas as pd
import database as db
import streamlit.components.v1 as components
from alphaagent import query_agent, create_agent, write_response, decode_response
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import StreamlitChatMessageHistory, ConversationBufferMemory
from langchain.utilities import WolframAlphaAPIWrapper, GoogleSearchAPIWrapper
import streamlit_authenticator as stauth
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
#############################################################################


############ Set up page configuration and favicon ################
basewidth = 600
favicon = Image.open("static/alpha.png")
wpercent = (basewidth / float(favicon.size[0]))
hsize = int((float(favicon.size[1]) * float(wpercent)))
img = favicon.resize((basewidth, hsize), Image.LANCZOS)
img.save('static/resized_image.png')

st.set_page_config(
    page_title="Alpha-Assist",
    page_icon= img,
    layout="centered",
    initial_sidebar_state="expanded")
#####################################################################


########### Setup api Keys ###################################
ZAPIER_CLIENT_SECRET = st.secrets["ZAPIER_CLIENT_SECRET"]
ZAPIER_CLIENT_ID = st.secrets["ZAPIER_CLIENT_ID"]
ZAPIER_NLA_API_KEY = st.secrets["ZAPIER_NLA_API_KEY"]
openai.api_key = st.secrets["OPENAI_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
WOLFRAM_ALPHA_APPID = st.secrets["WOLFRAM_ALPHA_APPID"]
GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
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
    with st.sidebar:
        st.title(f"Welcome {name}")
    data = st.sidebar.file_uploader("Upload a File")
    st.write(f'Welcome *{st.session_state["name"]}*')
    
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password') 
#####################################################################


################## Create Agent's Conversational Buffer Memory ###########################
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output")
##########################################################################################


############ Create LLMs (Language Models) / Agents / Special Tools  #######################
zapier = ZapierNLAWrapper()
wolfram = WolframAlphaAPIWrapper()
search = GoogleSearchAPIWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
llm = ChatOpenAI(temperature=0.6, streaming = True)
llm2 = OpenAI(temperature = 0)
agent2 = initialize_agent(toolkit.get_tools(), llm2, agent="zero-shot-react-description", verbose = True)

###########################################################################################
    

######################### Agent Toolkit #################################
tools = [
    Tool(
        name="Google Search",
        func=search.run,
        description="Useful for answering questions about current events, people, places."
    ),
    Tool(
        name="Wolfram Search",
        func=wolfram.run,
        description="Useful for answering questions about math, science, weather, date, and time."
    ),
    Tool(
        name="Email Agent",
        func= agent2.run,
        description="Useful for checking emails, drafting emails, and sending emails."
    ),
    Tool(
        name="Calendar Agent",
        func= agent2.run,
        description="Useful for checking calendar, user schedule, adding meetings and events, and creating new calendars."
    ),
    Tool(
        name="Google Docs Agent",
        func= agent2.run,
        description="Useful for searching for documents in google docs."
    ),
    Tool(
        name="DataViz Agent",
        func= agent2.run,
        description="Useful for creating tsbles, bar graphs, and line graphs."
    ),
]
###########################################################################################


############# Generate Agent Response With Conversational Langchain Agent ################
def generate_response(prompt):
    agent1 = initialize_agent(
            tools, 
            llm, 
            agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
            verbose = True, handle_parsing_errors = True, 
            memory = memory)

    message = agent1(prompt)
    return message["output"]
#########################################################################################


####################### Function to move focus to chat input ################################
def move_focus():
    # inspect the html to determine which control to specify to receive focus (e.g. text or textarea).
    st.components.v1.html(
        f"""
            <script>
                var textarea = window.parent.document.querySelectorAll("textarea[type=textarea]");
                for (var i = 0; i < textarea.length; ++i) {{
                    textarea[i].focus();
                }}
            </script>
        """,
    )
#################################################################################################

    
################ Function to complete messages using LLM  ##################
def complete_messages(nbegin, nend, stream=False):
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    with st.spinner(f"Waiting for {nbegin}/{nend} responses from Alpha."):
        if stream:
            responses = []
            for message in messages:
                prompt = message["content"]
                assistant_content = generate_response(prompt)  # Use your LLM to generate response
                responses.append(assistant_content)
            response_content = "".join(responses)
        else:
            response = generate_response(messages[-1]["content"])  # Use LLM to generate response
            response_content = response
    return response_content
##############################################################################################
    
    
################# Initialize Session States #######################################
def main():
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []
       # Create session state variables for tabs 2, 3, and 4
    if "tab2_content" not in st.session_state:
        st.session_state.tab2_content = []
    if "tab3_content" not in st.session_state:
        st.session_state.tab3_content = []
    if "tab4_content" not in st.session_state:
        st.session_state.tab4_content = []    
###################################################################################

 
############# Check User Authentication Status (Main Entrypoint) ###############
    
    if authentication_status:
################################################################################

        
########################## Tab Menu   ########################## 
        ChatBot = st.container()
        with ChatBot:
            st.title("Chat With Alpha")
            st.text("Intelligent chatbot with access to the web \nAsk Alpha questions or upload a file to get insights")
            tab1,tab2, tab3, tab4 = st.tabs(["AlphaChat","Basic Graphs","Data Profiler", "Insights Builder"])
#############################################################################################


######################## Tab1 - AlphaChat ###################################################
        with tab1:
            st.title("AlphaChat")
            st.text ("Chat History:")
            for i, message in enumerate(st.session_state.messages):
                nkey = int(i/2)
                if message["role"] == "user":
                    streamlit_chat.message(message["content"], is_user=True, avatar_style="avataaars", seed="24", key='chat_messages_user_'+str(nkey))
                else:
                    streamlit_chat.message(message["content"], is_user=False, avatar_style="bottts-neutral", seed="Aneka", key='chat_messages_assistant_'+str(nkey))

        if user_content := st.chat_input("Hello, my name is Alpha. Type your questions here.", key = "main_chat_input"): 
            with tab1:
                nkey = int(len(st.session_state.messages)/2)
                streamlit_chat.message(user_content, is_user=True,  avatar_style="avataaars", seed="24", key='chat_messages_user_'+str(nkey))
                st.session_state.messages.append({"role": "user", "content": user_content})
                assistant_content = complete_messages(0,1)
                streamlit_chat.message(assistant_content, avatar_style="bottts-neutral", seed="Aneka", key='chat_messages_assistant_'+str(nkey))
                st.session_state.messages.append({"role": "assistant", "content": assistant_content})
##############################################################################################
  

####################  TAB 2 - Dataviz Basic Implementation Tab ########################### 
        with tab2:
            st.title("Basic Graphs")
            #query = st.text_input("Insert your query")
            query = st.text_area("input data query here")
            if st.sidebar.button("Create Chart"):
                agent3 = create_agent(data)
                response = query_agent(agent=agent3, query=query)
                decoded_response = decode_response(response)
                #write_response(decoded_response)

                # Append the generated content (charts) to the Session State as "tab2_content"
                if "tab2_content" not in st.session_state:
                    st.session_state.tab2_content = []

                # Check if the response contains chart data and add it to the session state
                if "bar" in decoded_response or "line" in decoded_response or "table" in decoded_response:
                    st.session_state.tab2_content.append(decoded_response)

            # Display the content from Session State
            st.text("Chart History:")
            if st.session_state.tab2_content:
                for content in st.session_state.tab2_content:
                    write_response(content)
#######################################################################################
     
                
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
            if st.sidebar.button("Clear Conversation", key='clear_chat_button'):
                st.session_state.messages = []
            move_focus()
            authenticator.logout('Logout', 'sidebar',) 
            st.sidebar.write("[Terms of Service](https://docs.google.com/document/d/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)") 
            st.sidebar.write("[Privacy Policy](https://docs.google.com/document/d/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)") 
             
            
 ########################### Zapier OAUTH2 Implementation ###########################
 
            # Define your Zapier OAuth2 credentials
        ZAPIER_REDIRECT_URI = "https://calcifireconsulting.com"

        # Create a button in the sidebar to activate the agent
        st.sidebar.markdown(f'[Activate Agent](https://nla.zapier.com/oauth/authorize/?response_type=code&client_id={ZAPIER_CLIENT_ID}&redirect_uri={ZAPIER_REDIRECT_URI}&scope=nla%3Aexposed_actions%3Aexecute)')    
###########################################################################################                           
    
    else:
        st.write("# Welcome to Alpha Playground! 👋")

        #st.sidebar.success("Login and select the demo from above.")
        streamlit_chat.message("Hi. I'm Alpha, your friendly intelligent assistant. To get started, enter your username and password in the left sidebar.", avatar_style="bottts-neutral", seed="Aneka", key='intro_message_1')
        
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
######################################################################################
              
if __name__ == '__main__':
        main()       