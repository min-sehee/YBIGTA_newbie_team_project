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

# ---- 함수로 구성 ----
def analyze_review_csv(csv_path, shop_name=None):
    # 1. CSV 파일 불러오기
    df = pd.read_csv(csv_path)

    # 2. date 컬럼을 datetime으로 변환
    df['date'] = pd.to_datetime(df['date'])

    # 3. 최신순(날짜 내림차순) 정렬
    df = df.sort_values('date', ascending=False).reset_index(drop=True)

    # 4. 전체 연월 리스트(빈 월 포함) 생성 
    all_months = pd.period_range(
        start=df['year_month'].min(),
        end=df['year_month'].max(),
        freq='M'
    ).astype(str)

    # 5. 연월별 리뷰 개수 집계 (빈 월은 0으로)
    monthly_counts = df.groupby('year_month').size().reindex(all_months, fill_value=0).reset_index()
    monthly_counts.columns = ['year_month', 'review_count']

    # x축이 연-월 문자열이므로, datetime으로 변환
    monthly_counts['year_month_dt'] = pd.to_datetime(monthly_counts['year_month'])

    # ------ 파일명에서 서점 이름 자동 추출 (기본값은 None 사용) ------
    if not shop_name:
        shop_name = os.path.splitext(os.path.basename(csv_path))[0].replace('reviews_', '')

    return monthly_counts, shop_name

# 서점별 비교 분석 (여러 서점 비교)
def compare_review_trends(csv_paths):
    plt.figure(figsize=(14, 6))  # 그래프 크기 설정
    
    # 여러 서점의 CSV 파일을 읽어들여서 분석
    for csv_path in csv_paths:
        monthly_counts, shop_name = analyze_review_csv(csv_path)
        
        # 서점의 리뷰 수 변화를 라인으로 표시
        plt.plot(monthly_counts['year_month_dt'], monthly_counts['review_count'], label=shop_name)

    # 그래프 세부 설정
    plt.xlabel('연-월')
    plt.ylabel('리뷰 수')
    plt.title('서점별 연월 리뷰 개수 시계열 분석')
    plt.xticks(rotation=45)
    plt.legend(title='Stores')  # 서점명 표시
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 실행 예시: 여러 서점의 CSV 파일 경로를 리스트로 넘김
compare_review_trends([
    'database/preprocessed_reviews_aladin.csv',
    'database/preprocessed_reviews_kyobo.csv',
    'database/preprocessed_reviews_yes24.csv'
])
