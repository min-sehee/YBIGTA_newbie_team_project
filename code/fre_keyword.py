import os
import sys
import subprocess
import platform
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns

# 한글 폰트 설정
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'

font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# konlpy 설치 및 불러오기
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from konlpy.tag import Okt
except ImportError:
    print("[INFO] konlpy 설치 중...")
    install("konlpy")
    from konlpy.tag import Okt

from sklearn.feature_extraction.text import CountVectorizer

# 명사 토큰화 함수
def tokenize_korean_nouns(texts):
    okt = Okt()
    tokenized = []
    for text in texts:
        nouns = okt.nouns(text)
        tokenized.append(' '.join(nouns))
    return tokenized

# 서점별 주요 키워드 빈도 비교 + 막대그래프
def compare_korean_keywords_barplot(csv_paths, top_n=15):
    keyword_freqs = {}

    for path in csv_paths:
        df = pd.read_csv(path)
        reviews = df['review'].dropna().astype(str).tolist()
        reviewed_nouns = tokenize_korean_nouns(reviews)

        vectorizer = CountVectorizer(max_features=top_n)
        X = vectorizer.fit_transform(reviewed_nouns)
        keywords = vectorizer.get_feature_names_out()
        frequencies = X.toarray().sum(axis=0)

        site_name = os.path.basename(path).replace('reviews_', '').replace('.csv', '').capitalize()
        freq_df = pd.DataFrame({'keyword': keywords, site_name: frequencies})
        freq_df.set_index('keyword', inplace=True)
        keyword_freqs[site_name] = freq_df

    # 공통 키워드 기준 병합
    merged = pd.concat(keyword_freqs.values(), axis=1).fillna(0).astype(int)
    merged = merged.sort_values(by=merged.columns[0], ascending=False).head(top_n)

    # 막대그래프 시각화
    merged.plot(kind='bar', figsize=(14, 7), color=['skyblue', 'lightgreen', 'salmon'])
    plt.title(f'서점별 주요 키워드 빈도 비교 (명사 기준 Top {top_n})')
    plt.xlabel('키워드')
    plt.ylabel('빈도수')
    plt.xticks(rotation=45)
    plt.legend(title='서점')
    plt.tight_layout()
    plt.show()

    return merged

# ----------------------------
# 실행 예시
compare_korean_keywords_barplot([
    'database/preprocessed_reviews_aladin.csv',
    'database/preprocessed_reviews_kyobo.csv',
    'database/preprocessed_reviews_yes24.csv'
])
