import pandas as pd
import re
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import pandas as pd
import os

def build_faiss_index(csv_paths, save_path):
    # CSV 불러오기 및 합치기
    # 로컬에 클론한 GitHub 경로
    BASE_PATH = "YBIGTA_newbie_team_project/database"

    # 각 파일 경로
    aladin_csv = os.path.join(BASE_PATH, "preprocessed_reviews_aladin.csv")
    kyobo_csv = os.path.join(BASE_PATH, "preprocessed_reviews_kyobo.csv")
    yes24_csv = os.path.join(BASE_PATH, "preprocessed_reviews_yes24.csv")

    # 불러오기
    df_aladin = pd.read_csv(aladin_csv)
    df_kyobo = pd.read_csv(kyobo_csv)
    df_yes24 = pd.read_csv(yes24_csv)

    # 합치기
    df = pd.concat([df_aladin, df_kyobo, df_yes24], ignore_index=True)

    # 전처리
    def clean_text(text):
        text = str(text).strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s.,!?가-힣]", "", text)
        return text

    df = df.dropna(subset=["review"])
    df["review"] = df["review"].apply(clean_text)
    df = df[df["review"].str.len() >= 10]
    df = df.drop_duplicates(subset=["review"])

    documents = [Document(page_content=f"[리뷰] {row['review']}") for _, row in df.iterrows()]
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embedding)
    vectordb.save_local(save_path)
