from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.7,
        google_api_key="AIzaSyB_iCPFD-Foa-foavGsKL3HGZB7JLoeSiY"
    )
