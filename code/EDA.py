import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from datetime import datetime
import platform

# 한글 폰트 자동 설정
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

def review_eda(file_path):
    base = os.path.basename(file_path).lower()
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

    plt.figure(figsize=(16, 5))

    # 1. 별점 분포
    plt.subplot(1, 3, 1)
    sns.countplot(x='rating', data=df)
    plt.title(f'{shop_key} - 별점 분포')
    plt.xlabel('별점')
    plt.ylabel('개수')

    # 2. 리뷰 길이 분포
    plt.subplot(1, 3, 2)
    sns.histplot(df['review_len'], bins=30, kde=True)
    plt.title(f'{shop_key} - 리뷰 길이 분포')
    plt.xlabel('리뷰 길이')
    plt.ylabel('개수')

    # 3. 리뷰 작성일(날짜) 분포
    plt.subplot(1, 3, 3)
    sns.histplot(df['date'].dropna(), bins=30)
    plt.title(f'{shop_key} - 리뷰 작성일 분포')
    plt.xlabel('날짜')
    plt.ylabel('개수')

    plt.tight_layout()
    plt.show()

def visualize_outliers(input_data, rating_min=1, rating_max=5, reviewlen_short=10, reviewlen_long=300, min_year=2010):
    # 파일 경로로 전달된 경우 자동 로딩 및 shop_key 세팅
    if isinstance(input_data, str):
        df = pd.read_csv(input_data)
        base = os.path.basename(input_data).lower()
        if 'aladin' in base:
            shop_key = '알라딘'
        elif 'kyobo' in base:
            shop_key = '교보'
        elif 'yes24' in base:
            shop_key = '예스24'
        else:
            shop_key = os.path.splitext(base)[0]
    else:
        df = input_data.copy()
        shop_key = '리뷰 데이터'

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

    plt.figure(figsize=(12, 8))
    
    # 1. 별점 이상치 시각화
    plt.subplot(221)
    rating_counts = df['rating'].value_counts().sort_index()
    colors = ['red' if (r < rating_min or r > rating_max) else 'skyblue' for r in rating_counts.index]
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette=colors)
    plt.title(f'{shop_key} - 별점 이상치 (빨간색)')
    plt.xlabel('별점')
    plt.ylabel('개수')

    # 2. 리뷰 길이 이상치 시각화
    plt.subplot(222)
    sns.boxplot(y=df['review_len'])
    plt.title(f'{shop_key} - 리뷰 길이 이상치 (상자 밖 점)')
    plt.ylabel('리뷰 길이')

    # 3. 전체 날짜 분포 시각화
    plt.subplot(223)
    dates = df['date'].dropna()
    sns.histplot(dates, bins=30, color='skyblue')
    plt.title(f'{shop_key} - 전체 날짜 분포')
    plt.xlabel('날짜')
    plt.ylabel('개수')

    # 4. 날짜 이상치(과거/미래) 연-월별 시각화
    plt.subplot(224)
    outliers = pd.concat([out_past, out_future])
    outliers['year_month'] = outliers['date'].dt.to_period('M').astype(str)
    outlier_counts = outliers.groupby('year_month').size().reset_index(name='count')
    sns.barplot(data=outlier_counts, x='year_month', y='count', color='salmon')
    plt.title(f'{shop_key} - 날짜 이상치(과거/미래) 연-월별 분포')
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()

# 실행
review_eda('database/reviews_aladin.csv')
visualize_outliers('database/reviews_aladin.csv')
# review_eda('database/reviews_kyobo.csv')
# review_eda('database/reviews_yes24.csv')
