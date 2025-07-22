import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager, rc
import seaborn as sns
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

# ---- 함수 구성 ----
def analyze_review_csv(csv_path, shop_name=None):
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df = df.sort_values('date', ascending=False).reset_index(drop=True)

    all_months = pd.period_range(
        start=df['year_month'].min(),
        end=df['year_month'].max(),
        freq='M'
    ).astype(str)

    monthly_counts = df.groupby('year_month').size().reindex(all_months, fill_value=0).reset_index()
    monthly_counts.columns = ['year_month', 'review_count']

    total_reviews = monthly_counts['review_count'].sum()
    monthly_counts['review_percent'] = (monthly_counts['review_count'] / total_reviews) * 100
    monthly_counts['year_month_dt'] = pd.to_datetime(monthly_counts['year_month'])

    if not shop_name:
        shop_name = os.path.splitext(os.path.basename(csv_path))[0].replace('reviews_', '')

    return monthly_counts, shop_name

# 서점별 비교 분석
def compare_review_trends(csv_paths):
    plt.figure(figsize=(14, 6))
    
    for csv_path in csv_paths:
        monthly_counts, shop_name = analyze_review_csv(csv_path)
        plt.plot(monthly_counts['year_month_dt'], monthly_counts['review_percent'], label=shop_name)

    plt.xlabel('연-월')
    plt.ylabel('리뷰 비율 (%)')
    plt.title('서점별 연월 리뷰 비율 시계열 분석')
    plt.xticks(rotation=45)
    plt.legend(title='Stores')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# 실행 예시: 여러 서점의 CSV 파일 경로를 리스트로 넘김
compare_review_trends([
    'database/preprocessed_reviews_aladin.csv',
    'database/preprocessed_reviews_kyobo.csv',
    'database/preprocessed_reviews_yes24.csv'
])
