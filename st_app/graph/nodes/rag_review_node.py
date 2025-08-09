from st_app.rag.llm import get_llm
from st_app.rag.retriever import load_faiss_retriever
from st_app.rag.prompt import rag_prompt
from st_app.utils.state import ChatState
from st_app.rag.prompt import rag_prompt
from langchain.chains import RetrievalQA
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# LLM과 retriever 초기화
llm = get_llm()
retriever = load_faiss_retriever()

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": rag_prompt},
    input_key="question"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "대화 이력을 참고해 마지막 사용자 질문을 스탠드얼론 한국어 질문으로 간결히 재작성해."),
    MessagesPlaceholder("chat_history"),
    ("human", "{user_input}")
])
chain = prompt | llm

def rag_review_node(state: ChatState) -> ChatState:
    user_input = state.user_input
    chat_history = state.chat_history  # List[str]

    # LangChain 형식으로 변환
    lc_chat_history = []
    for line in chat_history:
        if line.startswith("User:"):
            lc_chat_history.append(HumanMessage(content=line[6:]))
        elif line.startswith("Bot:"):
            lc_chat_history.append(AIMessage(content=line[5:]))

    # 질문 재작성
    rewritten = chain.invoke({
        "chat_history": lc_chat_history,
        "user_input": user_input
    }).content.strip()

    # RAG 호출
    result = qa_chain.invoke({
        "question": rewritten,
        "chat_history": lc_chat_history
    })
    answer = result["result"]
    source_docs = result.get("source_documents", [])

    # source chunks 추출
    chunks = [doc.page_content for doc in source_docs]

    # chat history를 문자열 형식으로 업데이트
    updated_history = chat_history + [
        f"User: {user_input}",
        f"Bot: {answer}"
    ]

    return state.copy(update={
        "user_input": "",
        "chat_history": updated_history,
        "retreived_chunks": chunks,
        "rag_response": answer
    })
