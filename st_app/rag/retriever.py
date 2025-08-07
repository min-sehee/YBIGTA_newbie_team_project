from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_faiss_retriever(path="st_app/db/faiss_index", k=5):
    embedding = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")
    vectordb = FAISS.load_local(path, embedding, allow_dangerous_deserialization=True)
    return vectordb.as_retriever(search_kwargs={"k": k})
