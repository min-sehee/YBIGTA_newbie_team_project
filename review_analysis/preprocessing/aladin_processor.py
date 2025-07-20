# konlpy, pandas 등 외부 패키지 자동설치
import sys
import subprocess

def install(package, import_name=None):
    try:
        __import__(import_name or package)
        print(f"✅ {package} 설치되어 있음")
    except ImportError:
        print(f"📦 {package} 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("konlpy")
install("pandas")
install("scikit-learn", "sklearn")

# konlpy JDK 를 자동 다운로드해주지 않지만, pip로만 되는 서버/Google Colab/Jupyter에선 문제없이 사용 가능

from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Okt
from abc import ABC, abstractmethod
import pandas as pd
import os
import re
from review_analysis.preprocessing.base_processor import BaseDataProcessor

class AladinProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = None
        self.okt = Okt()

    def preprocess(self):

        print("알라딘 데이터 전처리 시작")
        self.df = pd.read_csv(self.input_path)

        # 결측치, 이상치 처리
        self.df.dropna(subset=['rating', 'review', 'date'], inplace=True)
        self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')
        self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df.dropna(subset=['date'], inplace=True)
        self.df['review'] = self.df['review'].astype(str)
        self.df['clean_review'] = self.df['review'].str.replace(r'[^\x00-\x7F\uAC00-\uD7A3\w\s]', '', regex=True)

        # 한글자·조사 포함 stopwords
        korean_stopwords = set([
            '이','그','저','것','수','들','좀','더','잘','많이','자주','같이','거의','너무','정말','그리고','또한',
            '하지만','그러나','때문에','그래서','거나','하며','하는','에는','ㅎㅎ','ㅋㅋ','ㅠㅠ','...','..','…','ㅡㅡ','~~','--',
            '거','다','까지','이다','입니다','있습니다','합니다','제','우리','그냥','또','다시','좀더','계속','항상','사실','보통',
            '대부분','혹시','요즘','더욱','의','가','이','은','는','을','를','에','도','와','한','과','로','에서','의','과','도','를','로서',
            '로써','에서','까지','에게','께서','만','밖에','보다','처럼','보다','까지','이며','하면서','으로','에게로','였다','했다','됐다','이다',
            '하게','하게끔','하게나','하기','해서','했더니','해서는','하고','하며','하고서도'
        ])

        def clean_and_tokenize(text):
            tokens = self.okt.morphs(text)
            filtered = [t for t in tokens if t not in korean_stopwords]
            return ' '.join(filtered)
        
        self.df['clean_review'] = self.df['clean_review'].apply(clean_and_tokenize)
        self.df = self.df[self.df['clean_review'].str.len() > 10]
        self.df = self.df[self.df['clean_review'].str.len() < 100]
        print(f"✅ 전처리 완료: {len(self.df)} rows")

    def feature_engineering(self):
        self.df['year_month'] = self.df['date'].dt.to_period('M').astype(str)
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform(self.df['clean_review'])
        print("✅ feature engineering 완료 / TF-IDF shape:", tfidf_matrix.shape)

    def save_to_database(self):
        self.df = self.df[['review', 'clean_review', 'rating', 'date', 'year_month']]
        os.makedirs(self.output_dir, exist_ok=True)
        save_path = os.path.join(self.output_dir, 'preprocessed_reviews_aladin.csv')
        self.df.to_csv(save_path, index=False)
        print("✅ 저장 완료 →", save_path)