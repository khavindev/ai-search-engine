import streamlit as st
import os
from fastapi import HTTPException
from pydantic import BaseModel
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

class SearchResult:
    def __init__(self, url: str, title: str, content: str):
        self.url = url
        self.title = title
        self.content = content

class SearchEngine:
    def __init__(self, tavily_api_key: str, groq_api_key: str, model_name: str):
        self.tavily_api_key = tavily_api_key
        self.groq_api_key = groq_api_key
        self.model_name = model_name

        # Set the API keys in the environment
        os.environ["TAVILY_API_KEY"] = self.tavily_api_key
        os.environ["GROQ_API_KEY"] = self.groq_api_key

        # Initialize the TavilySearchAPIRetriever
        self.tavily_retriever = TavilySearchAPIRetriever(k=3)

        # Set up the chatbot chain
        self.prompt = ChatPromptTemplate.from_template(
            """You are a intelligent search agent who can provide comprehensive answers to any user query developed by TextFusion.AI The agent should answer the question based only on the context provided. Make the answer as comprehensive as possible. Use citations for the sources.

            Context: {context}

            Question: {question}"""
        )

        self.chain = (
            RunnablePassthrough.assign(context=(lambda x: x["question"]) | self.tavily_retriever)
            | self.prompt
            | ChatGroq(temperature=0, model_name=self.model_name, groq_api_key=self.groq_api_key)
            | StrOutputParser()
        )

    def search(self, query: str) -> str:
        try:
            response = self.chain.invoke({"question": query})
            return response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

# Custom CSS loading functions
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

# Streamlit app
def main():
    st.set_page_config(page_title="TextFusion.AI Search", layout="wide")

    # Load custom CSS
    local_css("style.css")
    remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

    st.title("TextFusion.AI Intelligent Search")

    # Custom search bar
    icon("search")
    query = st.text_input("", "Search...")
    button_clicked = st.button("OK")

    # Initialize SearchEngine
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY)

    search_engine = SearchEngine(
        tavily_api_key=TAVILY_API_KEY,
        groq_api_key=GROQ_API_KEY,
        model_name="mixtral-8x7b-32768"
    )

    # Handle search query
    if button_clicked and query != "Search...":
        with st.spinner("Searching..."):
            result = search_engine.search(query)
        st.subheader(f"Search results for: '{query}'")
        st.write(result)

if __name__ == "__main__":
    main()