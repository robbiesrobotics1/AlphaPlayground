import streamlit as st
import openai
import streamlit.components.v1 as components
from PIL import Image
import streamlit_authenticator as stauth
import database as db
from langchain.memory import StreamlitChatMessageHistory, ConversationBufferMemory
import streamlit_chat 

# Set up page configuration and favicon
basewidth = 600
favicon = Image.open("static/alpha.png")
wpercent = (basewidth / float(favicon.size[0]))
hsize = int((float(favicon.size[1]) * float(wpercent)))
img = favicon.resize((basewidth, hsize), Image.LANCZOS)
img.save('static/resized_image.png')
st.set_page_config(
    page_title="Alpha-Assist",
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded"
)

# User Authentication Creation
users = db.fetch_all_users()
usernames = [user["key"] for user in users]
names = [user["name"] for user in users]
hashed_passwords = [user["password"] for user in users]
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "AlphaChat", "abcdef", cookie_expiry_days=1)
name, authentication_status, username = authenticator.login("Login", "sidebar")

# Authentication Status Conditionals
if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.sidebar.warning('Please enter your username and password')


# Create Agent's Conversational Buffer Memory
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)


def main():
    # Check User Authentication Status (Main Entry point)
    if authentication_status:
        # Image generation function from the first message
        def generate_messages(prompt):
            response = openai.Image.create(
                prompt=prompt,
                n=number_of_images,
                size=image_size
            )

            image_urls = []

            if 'data' in response and len(response['data']) > 0:
                for data_item in response['data']:
                    if 'url' in data_item:
                        image_urls.append(data_item['url'])

            if image_urls:
                return image_urls
            else:
                return ["Image generation failed"] * 4

        # Initialize Session States
        if "images" not in st.session_state:
            st.session_state.images = []

        number_of_images = st.sidebar.selectbox("Choose Number of Images", (1, 2, 3, 4))
        image_size = st.sidebar.selectbox("Choose Image Resolution", ("256x256", "512x512", "1024x1024"))

        # Create Tab Menu
        ChatBot = st.container()
        with ChatBot:
            st.title("Chat With Alpha")
            st.text("Intelligent chatbot with access to the web \nAsk Alpha questions or upload a file to get insights")

            st.text("Chat History:")
            for i, message in enumerate(st.session_state.images):
                if message["role"] == "user":
                    streamlit_chat.message(message["content"], is_user=True, avatar_style="avataaars", seed="24")
                else:
                    streamlit_chat.message(message["content"], is_user=False, avatar_style="avataaars-neutral", seed="Aneka114")

        if user_content := st.chat_input("Hello, my name is Alpha. Type your questions here.", key="main_chat_input"):
            with ChatBot:
                st.session_state.images.append({"role": "user", "content": user_content})
                assistant_content = generate_messages(user_content)
                streamlit_chat.message(user_content, is_user=True, avatar_style="avataaars", seed="24")

                if assistant_content and not all(url.startswith("Image generation failed") for url in assistant_content):
                    for url in assistant_content:
                        if not url.startswith("Image generation failed"):
                            st.session_state.images.append({"role": "assistant", "content": url})
                            streamlit_chat.message(url, is_user=False, avatar_style="avataaars-neutral", seed="Aneka114")
                        else:
                            st.session_state.images.append({"role": "assistant", "content": "Image generation failed. Please try again."})
                            streamlit_chat.message("Image generation failed. Please try again.", is_user=False, avatar_style="avataaars-neutral", seed="Aneka114")

        def reset_history():
            st.session_state["images"] = []
            
        st.sidebar.button("Clear Conversation", key='clear_chat_button', on_click=reset_history)
        authenticator.logout('Logout', 'sidebar',)
        st.sidebar.write("[Terms of Service](https://docs.google.com/document/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)")
        st.sidebar.write("[Privacy Policy](https://docs.google.com/document/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)")

    else:
        st.write("# Welcome to Alpha Playground! 👋")

        streamlit_chat.message("Hi. I'm Alpha, your friendly intelligent assistant. To get started, enter your username and password in the left sidebar.", avatar_style="avataaars-neutral", seed="Aneka114")

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


if __name__ == '__main__':
    main()
