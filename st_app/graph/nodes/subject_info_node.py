import json
from langchain.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm  # 경로 주의
from st_app.utils.state import ChatState

# 1. JSON 파일 로딩
with open("st_app/db/subject_information/subjects.json", "r", encoding="utf-8") as f:
    subject_data = json.load(f)

# 2. LLM 로딩
llm = get_llm()

# 3. 프롬프트 템플릿 정의
template = ChatPromptTemplate.from_template("""
당신은 책의 정보를 요약해서 사용자에게 설명하는 책 소개 도우미입니다.

사용자의 질문: "{query}"

아래는 '{title}'에 대한 정보입니다:

{book_info}

사용자의 질문에 맞춰 필요한 정보만 자연스럽게 알려주세요.
불필요한 정보는 포함하지 마세요.
""")

# 4. 노드 함수
def subject_info_node(state: ChatState) -> ChatState:
    query = state.user_input
    book_title = "소년이 온다"  # 현재는 하드코딩, 이후 subject 추출 로직으로 확장 가능

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

    # 정보가 있는 경우
    book_info = json.dumps(subject_data, ensure_ascii=False, indent=2)

    prompt = template.format_messages(
        query=query,
        title=book_title,
        book_info=book_info
    )

    response = llm(prompt).content

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