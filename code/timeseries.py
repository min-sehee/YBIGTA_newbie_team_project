import pandas as pd
import matplotlib.pyplot as plt
import os

# ---- 함수로 구성 ----
def analyze_review_csv(csv_path):
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

    # ------ 파일명에서 서점 이름 자동 추출 ------
    import os
    shop_name = os.path.splitext(os.path.basename(csv_path))[0].replace('reviews_', '')

    # 6. 시각화
    import matplotlib.pyplot as plt
    plt.figure(figsize=(14,6))
    plt.bar(monthly_counts['year_month_dt'], monthly_counts['review_count'],
            color='skyblue', alpha=0.6, label='Review count (Bar)')
    plt.plot(monthly_counts['year_month_dt'], monthly_counts['review_count'],
             color='red', label='Trend (Line)')

    plt.xlabel('Year-Month')
    plt.ylabel('Number of Reviews')
    plt.title(f'Monthly Review Counts ({shop_name.capitalize()})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return monthly_counts  # 필요시 집계 데이터 반환

analyze_review_csv("database/preprocessed_reviews_aladin.csv")
# analyze_review_csv("database/preprocessed_reviews_.csv")
# analyze_review_csv("database/preprocessed_reviews_.csv")
