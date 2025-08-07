from langgraph.graph import StateGraph
from st_app.utils.state import ChatState
from st_app.graph.nodes.chat_node import chat_node
from st_app.graph.nodes.subject_info_node import subject_info_node
from st_app.graph.nodes.rag_review_node import rag_review_node
from st_app.rag.llm import get_llm

def routing_llm(state: ChatState) -> str:
    """사용자의 입력을 기반으로 다음 실행할 노드를 LLM이 판단"""
    routing_prompt = f"""
    아래는 사용자와의 대화 내용입니다. 사용자의 최신 발화를 기반으로 다음 중 하나를 판단하세요:
    - "chat": 일반적인 대화 (잡담, 아무 주제 아님)
    - "subject": 사용자가 특정 주제/책/제품에 대해 알고 싶어함
    - "review": 사용자가 리뷰 기반의 요약, 평가, 분석 등을 알고 싶어함

    [대화 기록]
    {state.chat_history}

    [사용자 입력]
    {state.user_input}

    다음 중 하나의 키워드만 출력하세요: chat, subject, review
    """
    llm = get_llm()  
    decision = llm.invoke(routing_prompt).content.strip().lower()

    
    if decision not in ["chat", "subject", "review"]:
        return "chat_node" # fallback
    elif decision == "subject":
        return "subject_info_node"
    elif decision == "review":
        return "rag_review_node"
    else:
        return "chat_node"
    
def build_langgraph():
    builder = StateGraph(ChatState)
        
    builder.add_node("chat_node", chat_node)
    builder.add_node("subject_info_node", subject_info_node)
    builder.add_node("rag_review_node", rag_review_node)
        
    builder.set_entry_point("chat_node")
        
    builder.add_conditional_edges("chat_node", routing_llm, {
        "chat_node": "chat_node",
        "subject_info_node": "subject_info_node",
        "rag_review_node": "rag_review_node"
    })
        
    builder.add_edge("subject_info_node", "chat_node")
    builder.add_edge("rag_review_node", "chat_node")
        
    return builder.compile()