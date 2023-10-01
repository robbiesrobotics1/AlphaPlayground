####################         Imports      #######################################
import openai
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
import streamlit as st
from alphaagent import generate_response
import streamlit_authenticator as stauth
import database as db
#############################################################################

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
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.sidebar.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password')  
#####################################################################


####################### Create Memory ####################################
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output")
##########################################################################


if "messages" not in st.session_state:
        st.session_state.messages = [] 
        
            
##################### Reset Chat History Button ###########################
def reset_history():
        st.session_state.messages = [] 
###########################################################################        

################### Setup LLM Chain ################################################
template = """You are an AI assistant named Alpha having a conversation with st.session_state["name"]. If the user asks how you're feeling, you always respond with a new way to say that you are doing great!

{history}
Human: {human_input}
AI: """
prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
llm_chain = generate_response
###########################################################################################

####################  Main App #############################
def main():
    ############# Check User Authentication Status (Main Entrypoint) ###############  
    if authentication_status:
    ################################################################################
        ChatBot = st.container()
        with ChatBot:
            st.title("Chat With Alpha")
            st.text("An intelligent chatbot with access to the web. \nAsk Alpha questions or upload a file to get insights")
            st.text ("Chat History:")
#########################################################################################            
            
            
        ######################## Add Default Greeting ###############################################
        if len(msgs.messages) == 0:
            msgs.add_ai_message(f'Hello {st.session_state["name"]} , my name is Alpha! How can I help you?')
        ##########################################################################


################### Render current messages from StreamlitChatMessageHistory ##############
        
        for msg in msgs.messages:
            if msg.type == "human":
                st.chat_message("human").write(f'{st.session_state["name"]}: {msg.content}')
                st.session_state.messages.append({"role": "user", "content": msg.content})
            elif msg.type == "ai":
                st.chat_message("ai").write(f"Alpha: {msg.content}")
                st.session_state.messages.append({"role": "ai", "content": msg.content})
        ############################################################################################

     ######################### If user inputs a new prompt, generate and draw a new response ##########
        if prompt := st.chat_input():
            user_message = f'{st.session_state["name"]}: {prompt}'
            st.chat_message("human").write(user_message)
            ## Note: new messages are saved to history automatically by Langchain during run ##
            with st.spinner("Alpha is thinkng..."):
                response = llm_chain(prompt)
                ai_message = "Alpha: " + response
                st.chat_message("ai").write(ai_message)
        ############################################################################################
        
        
    ##############################################################################################
        authenticator.logout('Logout', 'sidebar',)
        st.sidebar.button("Clear Conversation", key='clear_chat_button', on_click=reset_history)
        st.sidebar.write("[Terms of Service](https://docs.google.com/document/d/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)") 
        st.sidebar.write("[Privacy Policy](https://docs.google.com/document/d/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)") 
    ####################################################################################################

    else:
        st.write(" Welcome to Alpha Playground! 👋")

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
    ######################################################################################
if __name__ == '__main__':
        main()                   
#apples and banannasa