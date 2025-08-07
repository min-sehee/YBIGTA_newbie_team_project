import json
from langchain.prompts import ChatPromptTemplate
from rag.llm import load_llm  # ✅ 기존 LLM import

# ✅ 1. JSON 파일 로딩
with open("st_app/db/subject_information/subjects.json", "r", encoding="utf-8") as f:
    subject_data = json.load(f)

# ✅ 2. LLM 불러오기
llm = load_llm()  # ✅ 재사용

# ✅ 3. 프롬프트 템플릿은 그대로
template = ChatPromptTemplate.from_template("""
당신은 책의 정보를 요약해서 사용자에게 설명하는 책 소개 도우미입니다.

사용자의 질문: "{query}"

아래는 '{title}'에 대한 정보입니다:

{book_info}

사용자의 질문에 맞춰 필요한 정보만 자연스럽게 알려주세요.
불필요한 정보는 포함하지 마세요.
""")

# ✅ 4. 노드 함수 정의
def subject_info_node(state):
    query = state["user_input"]
    book_title = "소년이 온다"

    if subject_data["title"] != book_title:
        return {
            "user_input": "",
            "chat_history": state["chat_history"] + [(query, "책 정보를 찾을 수 없습니다.")]
        }

    book_info = json.dumps(subject_data, ensure_ascii=False, indent=2)
    prompt = template.format_messages(query=query, title=book_title, book_info=book_info)
    response = llm(prompt).content

    return {
        "user_input": "",
        "chat_history": state["chat_history"] + [(query, response)]
    }
