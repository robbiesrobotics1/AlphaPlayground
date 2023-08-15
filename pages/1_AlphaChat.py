import os
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WolframAlphaAPIWrapper
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.agents import initialize_agent
from apikey import apikey, google_api_key, WOLFRAM_ALPHA_APPID
import streamlit as st

#Declare Environment Variables
os.environ['GOOGLE_API_KEY'] = google_api_key
os.environ['WOLFRAM_ALPHA_APPID'] = WOLFRAM_ALPHA_APPID
os.environ['OPENAI_API_KEY'] = apikey

#Create Conversational Buffer Memory
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)


##App Framework / Streamlit UI
Header=st.container()
ChatBot=st.container()

with Header:
    st.title('Alphabot Chat')
    st.text("Try out new features as they become available 😊", )

with ChatBot:
    st.header("Chat With Alpha")
    st.text("""GPT3.5 + Wolfram Alfa + Google Search=
    Intelligent chatbot with access to the web""")   
    prompt=st.text_input('Hello, my name is Alpha. How can I assist you?')


#Agent Available Tools
wolfram=WolframAlphaAPIWrapper()
search=GoogleSearchAPIWrapper(google_cse_id='56b5165f44e3a4d6d')
tools = [
    Tool(
        name = "Google Search",
        func=search.run,
        description="useful for when you need to answer questions about current events or the current state of the world"
    ),
    Tool(
        name = "Wolfram Search",
        func=wolfram.run,
        description="useful for when you need to answer questions about math, current date, time, and creating graphs"
    ),   
]


# Create LLMs
llm = ChatOpenAI(temperature=0.6, streaming=True)

#Create Agents
agent_chain = initialize_agent(tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True, memory=memory)

#Show to screen if prompted by user input
if prompt:
    response = agent_chain(prompt)
    
    st.write(response)
    