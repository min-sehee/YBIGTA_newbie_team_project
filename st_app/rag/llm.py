from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.7
    )


