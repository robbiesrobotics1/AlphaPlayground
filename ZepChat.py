from langchain.memory import ZepMemory
from langchain.retrievers import ZepRetriever
from langchain.llms import OpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.utilities import WikipediaAPIWrapper
from langchain.agents import initialize_agent, AgentType, Tool
from uuid import uuid4
import openai
import streamlit as st
from alphaagent import tools


# Set this to your Zep server URL
ZEP_API_URL = "http://localhost:8000"

session_id = str(uuid4())  # This is a unique identifier for the user
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set up Zep Chat History
memory = ZepMemory(
    session_id=session_id,
    url=ZEP_API_URL,
    memory_key="chat_history",
)

# Initialize the agent
llm = OpenAI(temperature=0)
agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

# Preload some messages into the memory. The default message window is 12 messages. We want to push beyond this to demonstrate auto-summarization.
test_history = [
    {"role": "human", "content": "Who was Octavia Butler?"},
    {
        "role": "ai",
        "content": (
            "Octavia Estelle Butler (June 22, 1947 – February 24, 2006) was an American"
            " science fiction author."
        ),
    },
    {"role": "human", "content": "Which books of hers were made into movies?"},
    {
        "role": "ai",
        "content": (
            "The most well-known adaptation of Octavia Butler's work is the FX series"
            " Kindred, based on her novel of the same name."
        ),
    },
    {"role": "human", "content": "Who were her contemporaries?"},
    {
        "role": "ai",
        "content": (
            "Octavia Butler's contemporaries included Ursula K. Le Guin, Samuel R."
            " Delany, and Joanna Russ."
        ),
    },
    {"role": "human", "content": "What awards did she win?"},
    {
        "role": "ai",
        "content": (
            "Octavia Butler won the Hugo Award, the Nebula Award, and the MacArthur"
            " Fellowship."
        ),
    },
    {
        "role": "human",
        "content": "Which other women sci-fi writers might I want to read?",
    },
    {
        "role": "ai",
        "content": "You might want to read Ursula K. Le Guin or Joanna Russ.",
    },
    {
        "role": "human",
        "content": (
            "Write a short synopsis of Butler's book, Parable of the Sower. What is it"
            " about?"
        ),
    },
    {
        "role": "ai",
        "content": (
            "Parable of the Sower is a science fiction novel by Octavia Butler,"
            " published in 1993. It follows the story of Lauren Olamina, a young woman"
            " living in a dystopian future where society has collapsed due to"
            " environmental disasters, poverty, and violence."
        ),
        "metadata": {"foo": "bar"},
    },
]


for msg in test_history:
    memory.chat_memory.add_message(
        HumanMessage(content=msg["content"])
        if msg["role"] == "human"
        else AIMessage(content=msg["content"]),
        metadata=msg.get("metadata", {}),
    )
    
if prompt := st.chat_input("Enter Your Messages Here"):
    st.chat_message("human").markdown(prompt)
    memory.chat_memory.add_message(HumanMessage(content=msg["content"]))
    zepchat = agent_chain(prompt)
    response = zepchat
    memory.chat_memory.add_message(AIMessage(content=msg["content"]))
    st.chat_message("ai").markdown(zepchat)