import os
import pandas as pd
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from review_analysis.preprocessing.base_processor import BaseDataProcessor

class Yes24Processor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df = pd.read_csv(self.input_path)
        self.output_path = os.path.join(self.output_dir, "preprocessed_reviews_yes24.csv")

    def preprocess(self):
        # 결측치 제거
        self.df.dropna(subset=['Rating', 'Date', 'Content'], inplace=True)

        # 이상치 처리: 별점 1~5만 허용
        self.df = self.df[self.df['Rating'].astype(str).str.isdigit()]
        self.df['Rating'] = self.df['Rating'].astype(int)
        self.df = self.df[(self.df['Rating'] >= 1) & (self.df['Rating'] <= 5)]

        # 날짜 전처리
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        self.df.dropna(subset=['Date'], inplace=True)

        # 리뷰 길이 파악 및 이상치 제거
        self.df['review_length'] = self.df['Content'].apply(len)
        self.df = self.df[(self.df['review_length'] >= 10) & (self.df['review_length'] <= 500)]

        # 텍스트 전처리 (간단한 예시)
        self.df['cleaned_content'] = self.df['Content'].apply(self.clean_text)

    def clean_text(self, text: str) -> str:
        # 특수문자 제거 + 소문자 변환
        text = re.sub(r"[^\w\s]", "", text)
        return text.lower()

    def feature_engineering(self):
        # 파생 변수: 요일, 년도+월
        self.df['weekday'] = self.df['Date'].dt.day_name()
        self.df['year_month'] = self.df['Date'].dt.to_period('M').astype(str)

        # TF-IDF 벡터화 (간단 예시)
        tfidf = TfidfVectorizer(max_features=100)
        tfidf_matrix = tfidf.fit_transform(self.df['cleaned_content'])

        # TF-IDF를 DataFrame으로 변환 후 기존 df와 concat (optional)
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
        self.df = pd.concat([self.df.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)

    def save_to_database(self):
        os.makedirs(self.output_dir, exist_ok=True)
        self.df.to_csv(self.output_path, index=False, encoding='utf-8-sig')
        print(f"Preprocessed CSV 저장 경로: {self.output_path}")
