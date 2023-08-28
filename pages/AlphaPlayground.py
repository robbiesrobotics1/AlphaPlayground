import os
from PIL import Image
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
import streamlit as st
import pygwalker as pyg
import pandas as pd
import streamlit.components.v1 as components
from alphaagent import query_agent, create_agent, write_response, decode_response
from langchain.agents import Tool, AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import StreamlitChatMessageHistory, ConversationBufferMemory
from langchain.utilities import WolframAlphaAPIWrapper, GoogleSearchAPIWrapper
from apikey import apikey, google_api_key, WOLFRAM_ALPHA_APPID, google_cse_id
from streamlit_chat import message

os.environ['OPENAI_API_KEY'] = apikey
os.environ['GOOGLE_API_KEY'] = google_api_key
os.environ['WOLFRAM_ALPHA_APPID'] = WOLFRAM_ALPHA_APPID
os.environ['GOOGLE_CSE_ID'] = google_cse_id

im = Image.open("alpha.png")

st.set_page_config(
    page_title="Calcifire Consulting - AlphaChat",
    page_icon=im,
    layout="wide"
)

# App Framework / Streamlit UI

ChatBot = st.container()

with ChatBot:
    st.header("Chat With Alpha")
    st.text("Intelligent chatbot with access to the web \nAsk Alpha questions or upload a file to get insights")
    tab1,tab2, tab3, tab4 = st.tabs(["AlphaChat","Basic Graphs","Data Profiler", "Insights Builder"])
    
# Agent Available Tools
wolfram = WolframAlphaAPIWrapper()
search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name="Google Search",
        func=search.run,
        description="Useful for answering questions about current events, people, places, or the world."
    ),
    Tool(
        name="Wolfram Search",
        func=wolfram.run,
        description="Useful for answering questions about math, date, and time."
    ),
   # Tool(
    #    name="Data Plotter",
   #     func=plotter.run,
    #    description="Useful for answering questions about data visualization and plotting graphs, tables, and charts."
   # ),
]


# Create Conversational Buffer Memory
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

# Create LLMs
llm = ChatOpenAI(temperature=0.6, streaming=True)

#Define how to send messages to LLM with streamlit caching
#@st.cache_data(show_spinner=False)
def generate_response(prompt):
    # Create Agents
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
        verbose=True, handle_parsing_errors=True, 
        memory=memory)

    message = agent(prompt)
    
    return message["output"]

if 'user' not in st.session_state:
    st.session_state['user'] = []


if 'generated' not in st.session_state:
    st.session_state['generated'] = []



def get_text():
    #input_text = st.text_input("Human [enter your message here]: "," Hello Mr AI how was your day today? ", key="input")
    input_text= st.chat_input('Hello, my name is Alpha. How can I assist you?''')
    return input_text 


user_input = get_text()

with tab1:
    if user_input:
        output = generate_response(user_input)
        st.session_state.user.append(user_input)  # Append user input at the end
        st.session_state.generated.append(output)  # Append generated response at the end

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state['user'][::-1][i], is_user=True, avatar_style="avataaars", seed="24", key=str(i) + '_user')
            message(st.session_state["generated"][::-1][i],avatar_style="bottts-neutral", seed="Aneka", key=str(i))
            
        
        
########################### Side Bar ############################  
  
#with st.sidebar:
      
    



########## Dataviz Basic Implementation Tab ###########################
with tab2:     
    data = st.file_uploader("Upload a CSV")

    query = st.text_area("Insert your query")

    if st.button("Submit Query"):
        # Create an agent from the CSV file.
        agent = create_agent(data)

        # Query the agent.
        response = query_agent(agent=agent, query=query)

        # Decode the response.
        decoded_response = decode_response(response)

        # Write the response to the Streamlit app.
        write_response(decoded_response)
        
        
 ######################### Data Profiler #################################################        
    with tab3:
        file = st.file_uploader("Upload File Here")
        if st.button("Get Data Profile"):
            df = pd.read_csv(file)
            pr = df.profile_report()
            st_profile_report(pr)
            
            
            
 ################### Insights Builder (Advanced DataViz) ###################          
with tab4:         
    csv_file= st.file_uploader("Upload Your CSV")

    if st.button("Explore Data"):
        # Import your data
        
        df = pd.read_csv(csv_file)
    
        # Generate the HTML using Pygwalker
        pyg_html = pyg.walk(df, return_html=True)
    
        # Embed the HTML into the Streamlit app
        components.html(pyg_html, height=1000, scrolling=True)
                
            
            
            
            
            
#with st.sidebar:
 #   if st.button("File Converter"):
      