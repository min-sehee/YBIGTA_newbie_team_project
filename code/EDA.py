import os
import sys
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns
from datetime import datetime
import platform

# 1. 필수 패키지 자동 설치
def install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('pandas')
install('matplotlib')
install('seaborn')

# 2. 한글 폰트 자동 설정
if platform.system() == 'Windows':
    font_path = 'C:/Windows/Fonts/malgun.ttf'
elif platform.system() == 'Darwin':
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
else:
    font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
try:
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)
except:
    pass
plt.rcParams['axes.unicode_minus'] = False

# 3. 통합 EDA/이상치 탐색 함수 (연-월별 날짜 시각화 포함)
def review_eda(file_path,
               rating_min=1, rating_max=5,
               reviewlen_short=10, reviewlen_long=500,
               min_year=2010):
    """
    file_path : 리뷰 csv 경로
    rating_min, rating_max: 별점 정상 범위 지정(예: 1~5)
    reviewlen_short: 너무 짧은 리뷰 간주 최소 글자수(미만시 이상치)
    reviewlen_long: 너무 긴 리뷰 간주 최대 글자수(초과시 이상치)
    min_year: 과거이상치 판단 기준(예: 2010년 이전)
    """
    # 서점명 자동 추출
    base = os.path.basename(file_path).lower()
    shop_key = None
    if 'aladin' in base:
        shop_key = '알라딘'
    elif 'kyobo' in base:
        shop_key = '교보'
    elif 'yes24' in base:
        shop_key = '예스24'
    else:
        shop_key = os.path.splitext(base)[0]

    df = pd.read_csv(file_path)
    for col in ['review', 'rating', 'date']:
        if col not in df.columns:
            raise ValueError(f"{col} 컬럼이 존재하지 않습니다. 파일 헤더를 확인해 주세요.")

    df['review'] = df['review'].astype(str)
    df['review_len'] = df['review'].apply(len)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 1. 분포 파악
    print("별점 분포:")
    print(df['rating'].value_counts().sort_index())
    sns.countplot(x='rating', data=df)
    plt.title(f'{shop_key} - 별점 분포')
    plt.xlabel('별점')
    plt.ylabel('개수')
    plt.show()

    print("텍스트 길이 분포:")
    sns.histplot(df['review_len'], bins=30, kde=True)
    plt.title(f'{shop_key} - 리뷰 길이 분포')
    plt.xlabel('리뷰 길이')
    plt.ylabel('개수')
    plt.show()

    print("날짜 분포:")
    sns.histplot(df['date'].dropna(), bins=30)
    plt.title(f'{shop_key} - 리뷰 작성일 분포')
    plt.xlabel('날짜')
    plt.ylabel('개수')
    plt.show()

    # 2. 이상치 파악
    print(f"\n[이상치 탐색]")
    # 별점 이상치
    out_rating = df[~df['rating'].between(rating_min, rating_max, inclusive='both')]
    print(f"별점 이상치 개수: {len(out_rating)}")
    if len(out_rating) > 0:
        print(out_rating[['review','rating','date']].head())
    plt.figure(figsize=(8, 5))
    rating_counts = df['rating'].value_counts().sort_index()
    colors = ['red' if (r < rating_min or r > rating_max) else 'skyblue' for r in rating_counts.index]
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette=colors)
    plt.title(f'{shop_key} - 별점 이상치 파악(이상치는 RED로, 정상은 BLUE)')
    plt.xlabel('별점')
    plt.ylabel('개수')
    plt.tight_layout()
    plt.show()

    # 리뷰 길이 이상치
    out_short = df[df['review_len'] < reviewlen_short]
    out_long = df[df['review_len'] > reviewlen_long]
    print(f"너무 짧은 리뷰 개수: {len(out_short)} 예시:")
    print(out_short[['review','review_len']].head())
    print(f"너무 긴 리뷰 개수: {len(out_long)} 예시:")
    print(out_long[['review','review_len']].head())
    sns.boxplot(y=df['review_len'])
    plt.title(f'{shop_key} - 리뷰 길이 이상치 파악')
    plt.ylabel('리뷰 길이')
    plt.show()

    # 날짜 이상치
    today = pd.Timestamp(datetime.today().date())
    out_past = df[(df['date'] < f'{min_year}-01-01') & (df['date'].notnull())]
    out_future = df[(df['date'] > today) & (df['date'].notnull())]
    print(f"과거 날짜 이상치({min_year}년 이전): {len(out_past)}")
    print(out_past[['review','date']].head())
    print(f"미래 날짜 이상치(오늘 이후): {len(out_future)}")
    print(out_future[['review','date']].head())
    
    # --- 날짜 이상치 시각화를 연-월별 막대그래프로! ---
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    count_by_ym = df.groupby('year_month').size().reset_index(name='count')
    plt.figure(figsize=(16, 6))
    sns.barplot(data=count_by_ym, x='year_month', y='count', color='skyblue')
    plt.xticks(rotation=45)
    plt.title(f'{shop_key} - 날짜 이상치 파악')
    plt.xlabel('연-월')
    plt.ylabel('개수')
    plt.tight_layout()
    plt.show()


# 실행 예시
review_eda('database/reviews_aladin.csv')
# review_eda('database/reviews_kyobo.csv')
# review_eda('database/reviews_yes24.csv')


def visualize_outliers(df, rating_min=1, rating_max=5, reviewlen_short=10, reviewlen_long=500, min_year=2010):
    # 전처리
    df['review_len'] = df['review'].apply(len)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # 이상치 추출
    out_rating = df[~df['rating'].between(rating_min, rating_max, inclusive='both')]
    out_short = df[df['review_len'] < reviewlen_short]
    out_long = df[df['review_len'] > reviewlen_long]
    today = pd.Timestamp(datetime.today().date())
    out_past = df[(df['date'] < f'{min_year}-01-01') & (df['date'].notnull())]
    out_future = df[(df['date'] > today) & (df['date'].notnull())]
    # 시각화
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(12, 8))
    plt.subplot(221)
    rating_counts = df['rating'].value_counts().sort_index()
    colors = ['red' if (r < rating_min or r > rating_max) else 'skyblue' for r in rating_counts.index]
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette=colors)
    plt.title('별점 이상치 (빨간색)')
    plt.xlabel('별점')
    plt.ylabel('개수')

    plt.subplot(222)
    sns.boxplot(y=df['review_len'])
    plt.title('리뷰 길이 이상치 (상자 밖 점)')
    plt.ylabel('리뷰 길이')

    plt.subplot(223)
    dates = df['date'].dropna()
    sns.histplot(dates, bins=30, color='skyblue')
    plt.title('전체 날짜 분포')
    plt.xlabel('날짜')
    plt.ylabel('개수')

    plt.subplot(224)
    outliers = pd.concat([out_past, out_future])
    outliers['year_month'] = outliers['date'].dt.to_period('M').astype(str)
    outlier_counts = outliers.groupby('year_month').size().reset_index(name='count')
    sns.barplot(data=outlier_counts, x='year_month', y='count', color='salmon')
    plt.title('날짜 이상치(과거/미래) 연-월별 분포')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()
