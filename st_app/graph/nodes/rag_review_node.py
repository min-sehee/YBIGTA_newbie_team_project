from st_app.rag.llm import get_llm
from st_app.rag.retriever import load_faiss_retriever
from langchain.chains import RetrievalQA

llm = get_llm()
retriever = load_faiss_retriever()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

def rag_review_node(state):
    query = state["user_input"]
    result = qa_chain({"query": query})
    answer = result["result"]

    return {
        "user_input": "",
        "chat_history": state["chat_history"] + [(query, answer)]
    }
