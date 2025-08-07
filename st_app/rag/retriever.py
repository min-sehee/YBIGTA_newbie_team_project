from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def load_faiss_retriever(path="st_app/db/faiss_index", k=5):
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.load_local(path, embedding, allow_dangerous_deserialization=True)
    return vectordb.as_retriever(search_kwargs={"k": k})
