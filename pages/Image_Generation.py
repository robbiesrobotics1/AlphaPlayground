import streamlit as st
import openai
import streamlit_chat
from PIL import Image
import streamlit.components.v1 as components
from langchain import OpenAI
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
    page_title="Alpha-Assist",
    page_icon= img,
    layout="wide",
    initial_sidebar_state="expanded")
#####################################################################

openai.api_key = st.secrets["OPENAI_API_KEY"]


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


#Main entry point when the user is authenticated
if authentication_status:
    number_of_images = st.sidebar.selectbox("Choose Number of Images",("1", "2", "3", "4"))
    image_size = st.sidebar.selectbox("Choose Image Resolution",("256x256", "512x512", "1024x1024"))
    def generate_messages(prompt):
        response = openai.Image.create(
            prompt=prompt,
            n = number_of_images,
            size=image_size
        )

        image_urls = []
        
        # Check if the response contains image URLs and extract them
        if 'data' in response and len(response['data']) > 0:
            for data_item in response['data']:
                if 'url' in data_item:
                    image_urls.append(data_item['url'])

        if image_urls:
            return image_urls 
        else:
            return ["Image generation failed"] * 4


  

    # Initialize the chat history
    if "images" not in st.session_state:
        st.session_state.images = []

    # Title for your Streamlit app
    st.title("Image Generation with Alpha")



    st.write("Chat History:")
    # Logout button and clear chat button
    authenticator.logout('Logout', 'sidebar',)
    if st.sidebar.button("Clear Conversation", key='clear_chat_button'):
        st.session_state.images = []

    # Links to terms of service and privacy policy
    st.sidebar.write("[Terms of Service](https://docs.google.com/document/d/e/2PACX-1vRsnJ_liUiUnyrysB380Thgcu-jBRZ57YQgvXusDVO11F4QGe49sea5iYV1SJuaSKDbg9D6OhXDqPMr/pub)")
    st.sidebar.write("[Privacy Policy](https://docs.google.com/document/e/2PACX-1vRGFn8CTVLdRdjmNJ9DPusSmiwcjfxDKO9K8yh0cyR_Zazb0kLGqv3gEoRhKOIOWxkWTOpPtUWXyeFt/pub)")

   # User input and response handling
    if user_content := st.chat_input("Type Your Image Prompt Here.", key="main_chat_input"):
        # Append the user's message to the chat history
        st.session_state.images.append({"role": "user", "content": user_content})
        
        # Generate images based on the user's input
        assistant_content = generate_messages(user_content)

        # Append the assistant's image responses to the chat history
        if assistant_content and not all(url.startswith("Image generation failed") for url in assistant_content):
            for url in assistant_content:
                if not url.startswith("Image generation failed"):
                    st.session_state.images.append({"role": "assistant", "content": url})
                else:
                    st.session_state.images.append({"role": "assistant", "content": "Image generation failed. Please try again."})
        else:
            error_message = "Image generation failed. Please try again."
            st.session_state.images.extend([{"role": "assistant", "content": error_message}] * 4)

   # ...

    # Display the chat history only when there are messages
    if st.session_state.images:
        chat_history_container = st.container()
        with chat_history_container:
            for i, message in enumerate(st.session_state.images):
                message_key = f"message_{i}"  # Generate a unique key for each message
                if message["role"] == "user":
                    streamlit_chat.message(
                        message["content"],
                        is_user=True,
                        avatar_style="avataaars",
                        seed="24",
                        key=message_key  # Pass the unique key here
                    )
                elif message["role"] == "assistant":
                    col1, col2, col3, col4 = st.columns(4)
                    if isinstance(message["content"], list) and len(message["content"]) >= 4:
                        with col1:
                            st.image(message["content"][0], use_column_width=False)
                        with col2:
                            st.image(message["content"][1], use_column_width=False)
                        with col3:
                            st.image(message["content"][2], use_column_width=False)
                        with col4:
                            st.image(message["content"][3], use_column_width=False)
                    elif isinstance(message["content"], str) and message["content"].startswith("http"):
                        # Display a single image
                        st.image(message["content"], use_column_width=False)
                        # Generate a unique key for the image based on the message key
                        image_key = f"image_{i}"
                        st.markdown(f'<div id="{image_key}"></div>', unsafe_allow_html=True)
                        st.markdown(f"""
                            <script>
                                document.getElementById("{image_key}").parentElement.parentElement.setAttribute("id", "{message_key}");
                            </script>
                        """, unsafe_allow_html=True)
                    else:
                        # Handle other message types
                        streamlit_chat.message(
                            message["content"],
                            is_user=False,
                            avatar_style="avataaars-neutral",
                            seed="Aneka114",
                            key=message_key  # Pass the unique key here
                        )

    # ...

# If the user is not authenticated
else:
    # Display an introductory message and authentication instructions
    streamlit_chat.message("Hi. I'm Alpha, your friendly intelligent assistant. To get started, enter your username and password in the left sidebar.",
                           avatar_style="avataaars-neutral", seed="Aneka114")

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
