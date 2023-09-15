############## Import Modules ############################################
import streamlit as st
import streamlit_chat
from PIL import Image
import database as db
import streamlit.components.v1 as components
from alphaagent import move_focus, complete_messages
import streamlit_authenticator as stauth
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
    layout="wide",
    initial_sidebar_state="expanded")
#####################################################################


########### Setup api Keys ###################################
ZAPIER_CLIENT_SECRET = st.secrets["ZAPIER_CLIENT_SECRET"]
ZAPIER_CLIENT_ID = st.secrets["ZAPIER_CLIENT_ID"]
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
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password') 
#####################################################################

def main():
    
################# Initialize Session States #######################################
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []   
###################################################################################

 
############# Check User Authentication Status (Main Entrypoint) ###############
    
    if authentication_status:
        
##########################   Create Tab Menu   ################################## 
        ChatBot = st.container()
        with ChatBot:
            st.title("Chat With Alpha")
            st.text("Intelligent chatbot with access to the web \nAsk Alpha questions or upload a file to get insights")
            
            st.text ("Chat History:")
            for i, message in enumerate(st.session_state.messages):
                nkey = int(i/2)
                if message["role"] == "user":
                    streamlit_chat.message(message["content"], is_user=True, avatar_style="avataaars", seed="24", key='chat_messages_user_'+str(nkey))
                else:
                    streamlit_chat.message(message["content"], is_user=False, avatar_style="avataaars-neutral", seed="Aneka114", key='chat_messages_assistant_'+str(nkey))

        if user_content := st.chat_input("Hello, my name is Alpha. Type your questions here.", key="main_chat_input"):
            with ChatBot:
                nkey = int(len(st.session_state.messages) / 2)
                user_key = 'chat_messages_user_' + str(nkey)
                assistant_key = 'chat_messages_assistant_' + str(nkey)

                streamlit_chat.message(user_content, is_user=True, avatar_style="avataaars", seed="24", key=user_key)
                st.session_state.messages.append({"role": "user", "content": user_content})
                assistant_content = complete_messages(0, 1)
                streamlit_chat.message(assistant_content, avatar_style="avataaars-neutral", seed="Aneka114", key=assistant_key)
                st.session_state.messages.append({"role": "assistant", "content": assistant_content})

        def reset_history():
            st.session_state["messages"] = [] 
            
##############################################################################################
        authenticator.logout('Logout', 'sidebar',)
        st.sidebar.button("Clear Conversation", key='clear_chat_button', on_click=reset_history)
        st.sidebar.write("[Terms of Service](https://docs.google.com/document/d/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)") 
        st.sidebar.write("[Privacy Policy](https://docs.google.com/document/d/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)") 
####################################################################################################


 ########################### Zapier OAUTH2 Implementation ###########################
 
            # Define your Zapier OAuth2 credentials
        ZAPIER_REDIRECT_URI = "https://calcifireconsulting.com"

        # Create a button in the sidebar to activate the agent
        st.sidebar.markdown(f'[Agent Access](https://nla.zapier.com/oauth/authorize/?response_type=code&client_id={ZAPIER_CLIENT_ID}&redirect_uri={ZAPIER_REDIRECT_URI}&scope=nla%3Aexposed_actions%3Aexecute)')    
###########################################################################################                           
    
    else:
        st.write("# Welcome to Alpha Playground! 👋")

        #st.sidebar.success("Login and select the demo from above.")
        streamlit_chat.message("Hi. I'm Alpha, your friendly intelligent assistant. To get started, enter your username and password in the left sidebar.", avatar_style="avataaars-neutral", seed="Aneka114", key='intro_message_1')
        
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