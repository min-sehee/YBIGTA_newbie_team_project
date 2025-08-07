from langchain.prompts import PromptTemplate

rag_prompt = PromptTemplate.from_template("""
다음 리뷰들을 참고하여 질문에 답하세요:

질문: {question}
리뷰:
{context}

답변:
""")
