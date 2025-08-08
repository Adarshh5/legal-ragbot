
from langchain.tools.retriever import create_retriever_tool

import os


from pydantic import BaseModel, Field
from typing import Literal
from langchain.tools import StructuredTool
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from pinecone import Pinecone
from langchain_ollama  import OllamaEmbeddings

from ddgs import DDGS

from langchain.tools import tool


load_dotenv() 


os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ['PINECONE_API_KEY']
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
model = ChatGroq(model="llama3-70b-8192")
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# VECTOR_DB_PATH = os.path.join(BASE_DIR, "./vector_db")

embedding_model = OllamaEmbeddings(model='nomic-embed-text')


pc = Pinecone(api_key=PINECONE_API_KEY)
#vectorstore = Chroma(
#     persist_directory=VECTOR_DB_PATH,
#     embedding_function=embedding_model
# )

vectorstore = PineconeVectorStore.from_existing_index(
    index_name=PINECONE_INDEX_NAME,
    embedding=embedding_model
)


retriever = vectorstore.as_retriever(search_kwargs={"k": 2})  # only top 1 chunk
 

@tool
def retrieve_legal_documents(query: str) -> str:
    """Given a user query, return the most relevant document chunk from Chroma."""
    docs = retriever.invoke(query)
    if not docs:
        return []
    return docs




@tool
def duckduckgo_search_tool(query: str) -> str:
    """Search the web using DuckDuckGo for legal chatbot updates or documents."""
    with DDGS() as ddgs:
        results = ddgs.text(query, region='wt-wt', safesearch='Off', max_results=3)
        if not results:
            return ""
        
        # You can also return the full list if needed
        response = ""
        for r in results:
            response += f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n\n"
        return response
    
    
   
tools = [retrieve_legal_documents, duckduckgo_search_tool]



