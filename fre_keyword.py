import subprocess
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import platform

#한글 폰트 설정 
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':  # macOS
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:  # (Linux 등)
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 깨짐 방지

# konlpy 자동 설치 및 불러오기(동일 파일에서만 실행하면 pip 명령어 입력 불필요)
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from konlpy.tag import Okt
except ImportError:
    print("[INFO] konlpy 패키지가 없어 설치를 시도합니다...")
    install("konlpy")
    from konlpy.tag import Okt

from sklearn.feature_extraction.text import CountVectorizer

def tokenize_korean_nouns(texts):
    okt = Okt()
    tokenized = []
    for text in texts:
        nouns = okt.nouns(text)
        tokenized.append(' '.join(nouns))
    return tokenized

def plot_korean_keywords(csv_path, top_n=20):
    # 데이터 불러오기
    df = pd.read_csv(csv_path)
    reviews = df['review'].dropna().astype(str).tolist()
    
    # 한글 명사만 추출하여 토큰화
    reviewed_nouns = tokenize_korean_nouns(reviews)
    
    # 키워드 빈도 집계
    vectorizer = CountVectorizer(max_features=top_n)
    X = vectorizer.fit_transform(reviewed_nouns)
    keywords = vectorizer.get_feature_names_out()
    frequencies = X.toarray().sum(axis=0)
    keyword_freq = pd.DataFrame({'keyword': keywords, 'frequency': frequencies}).sort_values(by='frequency', ascending=False)
    
    # 파일/서점명 자동 추출
    shop_name = os.path.basename(csv_path).replace('reviews_', '').replace('.csv', '').capitalize()
    
    # 시각화
    plt.figure(figsize=(12, 6))
    plt.bar(keyword_freq['keyword'], keyword_freq['frequency'], color='skyblue')
    plt.title(f'{shop_name} 도서 리뷰 키워드 빈도 (명사 기준 Top {top_n})')
    plt.xlabel('키워드')
    plt.ylabel('빈도')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    return keyword_freq

# ----------------------
plot_korean_keywords('database/reviews_aladin.csv')
# plot_korean_keywords('database/reviews_kyobo.csv')
# plot_korean_keywords('database/reviews_yes24.csv')
