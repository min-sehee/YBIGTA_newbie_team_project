from abc import ABC, abstractmethod
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import pandas as pd
import time
from utils.logger import setup_logger
from review_analysis.crawling.base_crawler import BaseCrawler

class AladinCrawler(BaseCrawler):
    """
    알라딘 전체 리뷰(별점, 날짜, 본문) 634개 크롤링 자동화 크롤러 (별점 정확히 파싱)
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.logger = setup_logger('aladin_crawler.log')
        self.reviews: list[str] = []
        self.ratings: list[float] = []
        self.dates: list[str] = [] 
        self.url = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=40869703&start=slayer#K662930932_CommentReview"

    def start_browser(self):
        """
        Selenium WebDriver 실행 및 리뷰 전체 탭 클릭
        """
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 테스트 중엔 주석
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.driver.get(self.url)
        time.sleep(2)
        # "전체" 탭 클릭 (id="tabTotal")
        try:
            total_tab = self.driver.find_element(By.ID, "tabTotal")
            self.driver.execute_script("arguments[0].click();", total_tab)
            self.logger.info("'전체' 탭 클릭 성공")
            time.sleep(2.5)
        except Exception as e:
            self.logger.warning("'전체' 탭 클릭 실패: " + str(e))

        self.logger.info("알라딘 전체 리뷰 탭 진입 완료")

    def scrape_reviews(self):
        """
        전체 리뷰 수집 ('리뷰 더보기' 반복 클릭, 스포일러 본문 포함, 별점 on만 카운트)
        """
        self.start_browser()
        prev_count = -1
        loop_count = 0

        while True:
            soup_pre = BeautifulSoup(self.driver.page_source, "html.parser")
            blocks_pre = soup_pre.select('div.hundred_list')
            cur_count = len(blocks_pre)
            try:
                more_wrap = self.driver.find_element(By.ID, "divReviewPageMore")
                more_btn = more_wrap.find_element(By.CSS_SELECTOR, "div.Ere_btn_more a")
                if more_btn.is_displayed() and more_btn.is_enabled():
                    self.logger.info(f"{loop_count+1}회 더보기 클릭 (현재 {cur_count}개)")
                    self.driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(2.3)
                    # AJAX가 붙을 때까지 대기
                    wait_try = 0
                    while wait_try < 7:
                        soup_now = BeautifulSoup(self.driver.page_source, "html.parser")
                        blocks_now = soup_now.select('div.hundred_list')
                        if len(blocks_now) > cur_count:
                            break
                        time.sleep(1)
                        wait_try += 1
                else:
                    self.logger.info("더보기 버튼이 비활성/없음으로 종료")
                    break
            except Exception:
                self.logger.info("더보기 버튼이 아예 없음/예외로 종료")
                break

            soup_after = BeautifulSoup(self.driver.page_source, "html.parser")
            after_count = len(soup_after.select('div.hundred_list'))
            if after_count == cur_count:
                self.logger.info(f"더보기 눌렀는데 리뷰 수가 늘지 않음 ({cur_count}), 루프 종료")
                break
            prev_count = cur_count
            loop_count += 1

        time.sleep(2)  # AJAX 최종 동기화

        # === 리뷰 파싱 ===
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        review_blocks = soup.select('div.hundred_list')
        total_collected = 0

        for block in review_blocks:
            try:
                # ⭐ 별점: 켜진 별만 카운트!
                star_div = block.select_one('.HL_star')
                rating = 0
                if star_div:
                    for img in star_div.find_all('img'):
                        if 'icon_star_on' in img.get('src', ''):
                            rating += 1

                # 리뷰 본문: 스포일러 안내문이 아닌 본문 찾기
                review = None
                review_spans = block.select('span[id^="spnPaper"]')
                for span in review_spans:
                    txt = span.text.strip()
                    if txt and not txt.startswith("이 글에는 스포일러가 포함되어 있습니다."):
                        review = txt
                        break
                if review is None and review_spans:
                    review = review_spans[0].text.strip()

                # 날짜: yyyy-mm-dd
                date = None
                for s in block.select('span.Ere_sub_gray8.Ere_fs13.Ere_PR10'):
                    text = s.text.strip()
                    if len(text) == 10 and text.count('-') == 2:
                        date = text
                        break

                if review and date and rating is not None:
                    self.reviews.append(review)
                    self.ratings.append(rating)
                    self.dates.append(date)
                    total_collected += 1
            except Exception as e:
                self.logger.warning(f"리뷰 파싱 중 오류: {e}")
                continue

        self.logger.info(f"총 {total_collected}건의 리뷰를 수집하였습니다.")

    def save_to_database(self):
        """
        크롤링한 리뷰 데이터를 database/reviews_aladin.csv로 저장
        """
        data = {
            'review': self.reviews,
            'rating': self.ratings,
            'date': self.dates
        }
        df = pd.DataFrame(data)
        output_path = f"{self.output_dir}/reviews_aladin.csv"
        df.to_csv(output_path, index=False)
        self.logger.info(f"{len(df)}건 리뷰를 {output_path}에 저장 완료")
