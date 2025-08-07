from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
import os
load_dotenv()

# 1. LLM 초기화 
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.environ["GOOGLE_API_KEY"]  # 여기를 명시해줘야 함!
)

# 2. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 사용자에게 친절하게 대답하는 AI 챗봇입니다. 사용자의 질문에 자연스럽게 한국어로 대답해주세요."),
    MessagesPlaceholder(variable_name="chat_history"), # 이전 대화 내용이 들어갈 자리
    ("human", "{user_input}"), # 현재 사용자의 입력이 들어갈 자리
])

# 3. LangChain 체인 구성
# 프롬프트와 LLM을 파이프(|)로 연결합니다.
chain = prompt | llm

# ✅ 4. 노드 함수 정의
def chat_node(state: dict) -> dict:
    """
    일반적인 대화를 처리하는 Chat Node 입니다.
    대화 기록(chat_history)을 바탕으로 답변을 생성합니다.
    """
    user_input = state["user_input"]
    chat_history = state["chat_history"]

    # 체인을 실행하여 LLM으로부터 응답을 받습니다.
    response = chain.invoke({
        "chat_history": chat_history,
        "user_input": user_input
    })

    # 새로운 대화 내용을 기록에 추가합니다.
    # HumanMessage와 AIMessage 객체로 저장해야 MessagesPlaceholder가 올바르게 인식합니다.
    updated_history = chat_history + [
        HumanMessage(content=user_input),
        AIMessage(content=response.content)
    ]

    # 업데이트된 상태를 반환합니다.
    return {
        "chat_history": updated_history,
        "last_response": response.content # 라우터나 UI에서 마지막 응답을 쉽게 사용하기 위함
    }

# --- 테스트용 코드 ---
if __name__ == '__main__':
    print("🤖 Chat Node 테스트 시작")

    # 초기 상태
    initial_state = {
        "user_input": "지금 시간이 몇 시야?",
        "chat_history": []
    }

    # 첫 번째 대화
    result1 = chat_node(initial_state)
    print("User:", initial_state["user_input"])
    print("AI:", result1["last_response"])

    print("\n--- 다음 대화 ---")

    # 두 번째 대화 (이전 대화를 기억하는지 확인)
    second_state = {
        "user_input": "내가 방금 뭐라고 물어봤지?",
        "chat_history": result1["chat_history"] # 이전 대화 기록을 넘겨줌
    }

    result2 = chat_node(second_state)
    print("User:", second_state["user_input"])
    print("AI:", result2["last_response"])