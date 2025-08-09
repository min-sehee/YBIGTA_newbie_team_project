from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st
import os


load_dotenv()


def get_llm():
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

    return ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.7,
        api_key = os.environ["GOOGLE_API_KEY"]
        )


