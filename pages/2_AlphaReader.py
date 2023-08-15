import os, tempfile
from filetype import guess
from langchain.document_loaders import UnstructuredCSVLoader,UnstructuredFileLoader, UnstructuredImageLoader
import streamlit as st, pinecone
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.pinecone import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.document_loaders import PyPDFLoader,DirectoryLoader,UnstructuredFileLoader,UnstructuredImageLoader,UnstructuredCSVLoader,UnstructuredEPubLoader
from apikey import apikey, pineconekey, pineconenv

#Declare Environment Variables
os.environ['OPENAI_API_KEY'] = apikey
os.environ['PINECONE_API_KEY'] = pineconekey
os.environ['PINECONE_ENV'] = pineconenv

#Memory
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

# Streamlit app
st.subheader('Alpha Reader - Chat With Documents')
source_doc = st.file_uploader("Upload source document", label_visibility="collapsed")
query = st.text_input("Enter your query")

if st.button("Submit"):
    # Validate inputs
    if not source_doc or not query:
        st.warning(f"Please upload the document and provide the missing fields.")
    else:
        try:
            # Save uploaded file temporarily to disk, load and split the file into pages, delete temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(source_doc.read())   
                
            loader = UnstructuredFileLoader(tmp_file.name)
            pages = loader.load_and_split()
            os.remove(tmp_file.name)
            
            # Generate embeddings for the pages, insert into Pinecone vector database, and expose the index in a retriever interface
            pinecone.init(api_key=pineconekey, environment=pineconenv)
            embeddings = OpenAIEmbeddings(openai_api_key=apikey)
            pinecone_index = "alphareader"
            vectordb = Pinecone.from_documents(pages, embeddings, index_name=pinecone_index)
            retriever = vectordb.as_retriever()

            # Initialize the OpenAI module, load and run the Retrieval Q&A chain
            llm = ChatOpenAI(temperature=0, openai_api_key=apikey)
            qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=retriever)
            response = qa.run(query)
            
            st.success(response)
        except Exception as e:
            st.error(f"An error occurred: {e}")