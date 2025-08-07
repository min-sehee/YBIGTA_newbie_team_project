pip install pandas faiss-cpu sentence-transformers langchain google-generativeai
pip install -U langchain-community
import pandas as pd
import faiss
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os

# 본인 키로 바꿔서 입력
os.environ["GOOGLE_API_KEY"] = "---"

from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 샘플 문장 임베딩
texts = ["이 책 정말 재미있어요.", "번역이 조금 아쉬웠어요."]
embeddings = embedding.embed_documents(texts)

print("임베딩 차원:", len(embeddings[0]))
print("임베딩 확인:", embeddings[0][:5])

import pandas as pd
import re
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# 📥 1. CSV 로딩 및 합치기
df1 = pd.read_csv("/content/drive/MyDrive/새폴더1/Dataset/preprocessed_reviews_yes24.csv")
df2 = pd.read_csv("/content/drive/MyDrive/새폴더1/Dataset/preprocessed_reviews_kyobo.csv")
df3 = pd.read_csv("/content/drive/MyDrive/새폴더1/Dataset/preprocessed_reviews_aladin.csv")
df = pd.concat([df1, df2, df3], ignore_index=True)

# 🧼 2. 전처리 함수 정의
def clean_text(text):
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)              # 공백 정리
    text = re.sub(r"[^\w\s.,!?가-힣]", "", text)   # 특수기호 제거 (이모지 등)
    return text

# 🎯 3. review 컬럼만 사용 + 전처리
df = df.dropna(subset=["review"])  # 결측치 제거
df["review"] = df["review"].apply(clean_text)
df = df[df["review"].str.len() >= 10]  # 너무 짧은 리뷰 제거
df = df.drop_duplicates(subset=["review"])  # 중복 제거

# 📄 4. Document로 변환
documents = [
    Document(page_content=f"[리뷰] {row['review']}")
    for _, row in df.iterrows()
]
print(f"📄 전처리 후 {len(documents)}개의 리뷰 사용됨")

# ✂️ 5. Chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"✂️ 총 {len(chunks)}개의 청크로 분할됨")

# 🧠 6. 임베딩 및 FAISS 인덱스 저장
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.from_documents(chunks, embedding)

save_path = "faiss_index_test"
vectordb.save_local(save_path)
print(f"✅ FAISS 인덱스 저장 완료 → {save_path}/")

!pip install --upgrade langchain
!pip install langchain-google-genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# ✅ 1. FAISS 인덱스 불러오기
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = FAISS.load_local(
    "faiss_index_test",
    embedding,
    allow_dangerous_deserialization=True
)


# ✅ 2. Gemini LLM 세팅
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.7
)

# ✅ 3. RAG QA 체인 구성
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    return_source_documents=True  # (선택) 근거도 같이 보기 위해
)
# ✅ 4. 테스트 질의
query = "리뷰에서 감동, 슬픔 중 어떤 감정이 더 많이 언급됐어?"
result = qa_chain({"query": query})

# ✅ 5. 결과 출력
print("💬 Gemini 응답:\n")
print(result["result"])

# (선택) 어떤 리뷰들이 근거로 쓰였는지 확인
print("\n📄 참고된 리뷰들:")
for doc in result["source_documents"]:
    print(" -", doc.page_content[:100], "...")

#----------------------------여기까지 RAG LLM -------------------------

# st_app/graph/nodes/subject_info_node.py

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# ✅ 1. JSON 파일 로딩
with open("/content/drive/MyDrive/새폴더1/Dataset/subjects.json", "r", encoding="utf-8") as f:
    subject_data = json.load(f)

# ✅ 2. LLM 초기화 (Gemini Flash 사용)
llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", temperature=0.7)

# ✅ 3. 프롬프트 템플릿 정의
template = ChatPromptTemplate.from_template("""
당신은 책의 정보를 요약해서 사용자에게 설명하는 책 소개 도우미입니다.

당신은 책 소개 도우미입니다.

사용자의 질문: "{query}"

아래는 '{title}'에 대한 정보입니다:

{book_info}

사용자의 질문에 맞춰 필요한 정보만 자연스럽게 알려주세요.
불필요한 정보는 포함하지 마세요.
""")

# ✅ 4. 노드 함수 정의
def subject_info_node(state):
    query = state["user_input"]
    book_title = "소년이 온다"  # (예시: 실제 사용 시엔 LLM으로 추출하거나 keyword 매칭)

    if subject_data["title"] != book_title:
        return {"user_input": "", "chat_history": state["chat_history"] + [(query, "책 정보를 찾을 수 없습니다.")]}

    # 책 정보 텍스트 구성
    book_info = json.dumps(subject_data, ensure_ascii=False, indent=2)

    # 프롬프트 채우기
    prompt = template.format_messages(query=query, title=book_title, book_info=book_info)

    # Gemini 응답 생성
    response = llm(prompt).content

    return {
        "user_input": "",
        "chat_history": state["chat_history"] + [(query, response)]
    }
state = {
    "user_input": "소년이 온다 출판사 알려줘",
    "chat_history": []
}

result = subject_info_node(state)
print(result["chat_history"][-1])

#------------------여기까지 subject LLM--------------
