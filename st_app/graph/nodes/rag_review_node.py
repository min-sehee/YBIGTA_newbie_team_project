from st_app.rag.llm import get_llm
from st_app.rag.retriever import load_faiss_retriever
from st_app.utils.state import ChatState
from st_app.rag.prompt import rag_prompt
from langchain.chains import RetrievalQA

# LLM과 retriever 초기화
llm = get_llm()
retriever = load_faiss_retriever()

# QA 체인 구성
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": rag_prompt},
    input_key="question"
)

def rag_review_node(state: ChatState) -> ChatState:
    query = state.user_input

    # 체인 실행
    result = qa_chain.invoke({"question": query})
    answer = result["result"]
    source_docs = result["source_documents"]

    # source chunks 추출 (문서 본문만)
    chunks = [doc.page_content for doc in source_docs]

    # chat history 업데이트
    updated_history = state.chat_history + [
        f"User: {query}",
        f"Bot: {answer}"
    ]

    # 상태 업데이트 및 반환
    return state.copy(update={
        "user_input": "",
        "chat_history": updated_history,
        "retreived_chunks": chunks,
        "rag_response": answer
    })