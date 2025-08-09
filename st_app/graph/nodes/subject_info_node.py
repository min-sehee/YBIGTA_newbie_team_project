import json
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from st_app.rag.llm import get_llm  
from st_app.utils.state import ChatState

# 1. JSON 파일 로딩
with open("st_app/db/subject_information/subjects.json", "r", encoding="utf-8") as f:
    subject_data = json.load(f)

# 2. LLM 로딩
llm = get_llm()

# 3. 프롬프트 템플릿 정의
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "너는 책 정보를 요약해 사용자 질문에 맞게 한국어로 간결·정확하게 답하는 도우미다. "
     "주어진 정보만 사용하고, 모르면 모른다고 말해라."),
    MessagesPlaceholder("chat_history"),
    ("human",
     '사용자의 질문: "{query}"\n\n'
     "아래는 '{title}'에 대한 정보다:\n\n"
     "{book_info}\n\n"
     "질문에 필요한 정보만 자연스럽게 답해줘. 불필요한 내용은 제외해.")
])

# 4. 노드 함수
def subject_info_node(state: ChatState) -> ChatState:
    query = state.user_input
    book_title = "소년이 온다" 

    if subject_data["title"] != book_title:
        # 정보 없음 응답
        updated_history = state.chat_history + [
            f"User: {query}",
            f"Bot: 책 정보를 찾을 수 없습니다."
        ]
        return state.copy(update={
            "user_input": "",
            "chat_history": updated_history
        })
    
    chat_history_str: list[str] = state.chat_history
    lc_chat_history = []
    for line in chat_history_str:
        if line.startswith("User:"):
            lc_chat_history.append(HumanMessage(content=line[6:].strip()))
        elif line.startswith("Bot:"):
            lc_chat_history.append(AIMessage(content=line[5:].strip()))

    # 정보가 있는 경우
    book_info = json.dumps(subject_data, ensure_ascii=False, indent=2)

    messages = prompt.format_messages(
        chat_history=lc_chat_history,
        query=query,
        title=book_title,
        book_info=book_info
    )
    response = llm.invoke(messages).content

    updated_history = state.chat_history + [
        f"User: {query}",
        f"Bot: {response}"
    ]

    return state.copy(update={
        "user_input": "",
        "chat_history": updated_history,
        "selected_subject": book_title,
        "subject_info": book_info
    })