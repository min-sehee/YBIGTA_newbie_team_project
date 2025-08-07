from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from st_app.rag.llm import get_llm

# 1. LLM 초기화 
llm = get_llm()

# 2. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 사용자에게 친절하게 대답하는 AI 챗봇입니다. 사용자의 질문에 자연스럽게 한국어로 대답해주세요."),
    MessagesPlaceholder(variable_name="chat_history"), # 이전 대화 내용이 들어갈 자리
    ("human", "{user_input}"), # 현재 사용자의 입력이 들어갈 자리
])

# 3. LangChain 체인 구성
chain = prompt | llm

# 4. 노드 함수 정의
def chat_node(state: dict) -> dict:
    """
    일반적인 대화를 처리하는 Chat Node
    대화 기록(chat_history)을 바탕으로 답변을 생성
    """
    user_input = state["user_input"]
    chat_history = state["chat_history"]

    # 체인을 실행하여 LLM으로부터 응답
    response = chain.invoke({
        "chat_history": chat_history,
        "user_input": user_input
    })

    # 새로운 대화 내용을 기록에 추가
    updated_history = chat_history + [
        HumanMessage(content=user_input),
        AIMessage(content=response.content)
    ]

    # 업데이트된 상태를 반환
    return {
        "chat_history": updated_history,
        "last_response": response.content
    }