from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from st_app.rag.llm import get_llm
from st_app.utils.state import ChatState  # ← 네가 정의한 상태 모델

# 1. LLM 초기화
llm = get_llm()

# 2. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 사용자에게 친절하게 대답하는 AI 챗봇입니다. 사용자의 질문에 자연스럽게 한국어로 대답해주세요."),
    MessagesPlaceholder(variable_name="chat_history"),  # LangChain message 객체 리스트
    ("human", "{user_input}")
])

# 3. LangChain 체인 구성
chain = prompt | llm

# 4. Chat Node 정의
def chat_node(state: ChatState) -> ChatState:
    """
    일반적인 대화를 처리하는 Chat Node
    """
    user_input = state.user_input
    chat_history = state.chat_history  # 이건 List[str] 타입이므로 아래에서 변환 필요

    # LangChain 형식으로 변환 (str → HumanMessage / AIMessage)
    lc_chat_history = []
    for line in chat_history:
        if line.startswith("User:"):
            lc_chat_history.append(HumanMessage(content=line[6:]))
        elif line.startswith("Bot:"):
            lc_chat_history.append(AIMessage(content=line[5:]))

    # LLM 호출
    response = chain.invoke({
        "chat_history": lc_chat_history,
        "user_input": user_input
    })

    # 대화 기록 업데이트 (str 포맷으로 저장)
    updated_history = chat_history + [
        f"User: {user_input}",
        f"Bot: {response.content}"
    ]

    # ChatState로 반환
    return state.copy(update={
        "user_input": "",
        "chat_history": updated_history
    })