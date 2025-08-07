import streamlit as st
from st_app.graph.router import build_langgraph  # 너가 만든 graph builder
from st_app.utils.state import ChatState

# LangGraph 실행기 초기화
graph_executor = build_langgraph()

# 세션 상태 초기화 (Streamlit 세션 내에 상태 보관)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = None

# 페이지 제목
st.title("📚 책 리뷰 기반 챗봇 (LangGraph RAG)")

# 사용자 입력 받기
user_input = st.text_input("질문을 입력하세요", key="user_input")

if user_input:
    # 현재 상태 구성
    state = ChatState(
        user_input=user_input,
        chat_history=st.session_state.chat_history,
        selected_subject=st.session_state.selected_subject
    )

    # LangGraph 실행
    next_state = graph_executor.invoke(state)

    # 세션 상태 업데이트
    st.session_state.chat_history = next_state.chat_history
    st.session_state.selected_subject = next_state.selected_subject

    # 출력
    st.markdown("### 💬 대화 기록")
    for line in st.session_state.chat_history:
        if line.startswith("User:"):
            st.markdown(f"**🙋 {line[6:]}**")
        elif line.startswith("Bot:"):
            st.markdown(f"🧠 {line[5:]}")
