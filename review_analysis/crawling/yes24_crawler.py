from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.logger import setup_logger
from bs4 import BeautifulSoup
import csv
import os

class Yes24Crawler(BaseCrawler):
    """
    YES24 한줄평 크롤러 (Selenium 기반)

    - 상품 고유 ID(goods_id)에 기반하여 YES24 도서의 한줄평을 수집합니다.
    - Selenium을 통해 AJAX 요청 페이지를 순차적으로 로드하고,
      BeautifulSoup으로 HTML을 파싱하여 리뷰 정보를 추출합니다.
    - 수집 항목: 평점, 작성일, 리뷰 내용, 공감 수
    - 수집된 데이터는 CSV 파일로 저장됩니다.
    """

    def __init__(self, output_dir: str):
        """
        크롤러 초기화
        """
        super().__init__(output_dir)
        self.base_url = 'https://www.yes24.com/product/goods/13137546'
        self.goods_id = '13137546'
        self.max_page = 328
        self.reviews: list[list[str]] = [] 
        self.driver = None
        self.logger = setup_logger('yes24_crawler.log')
        self.output_path = os.path.join(self.output_dir, 'reviews_yes24.csv')

    def start_browser(self):
        """
        Selenium Chrome 드라이버 실행 설정 및 시작
        """        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 필요 시 활성화
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_reviews(self):
        """
        YES24 한줄평 리뷰를 페이지 단위로 순회하며 수집

        - AJAX 방식으로 로드되는 각 리뷰 페이지에 접근
        - 리뷰 컨테이너가 로딩될 때까지 대기 후 HTML 파싱
        - 평점, 날짜, 내용, 공감 수를 추출하여 self.reviews 리스트에 저장
        - 리뷰가 없으면 크롤링 중단
        """
        self.start_browser()

        for page_num in range(1, self.max_page + 1):
            self.logger.info(f"한줄평 {page_num} 페이지 로드 중...")

            ajax_url = (
                f"https://www.yes24.com/Product/communityModules/AwordReviewList/{self.goods_id}"
                f"?goodsSetYn=N&sort=2&isFirstLoad=1&PageNumber={page_num}"
            )

            self.driver.get(ajax_url)

            try:
                # AJAX로 리뷰가 로딩될 때까지 최대 5초 기다림
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cmtInfoGrp"))
                )
            except Exception as e:
                self.logger.warning(f"페이지 {page_num} 로딩 실패: {e}")
                continue

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            review_boxes = soup.select("div.cmtInfoGrp")
            if not review_boxes:
                self.logger.info("리뷰 없음으로 인한 중단")
                break

            for box in review_boxes:
                try:
                    content = box.select_one("div.cmt_cont span.txt").text.strip()
                    rating_class = box.select_one("div.cmt_rating span.rating")["class"]
                    rating = next((c.replace("rating_", "") for c in rating_class if c.startswith("rating_")), None)
                    sympathy = box.select_one("a.btnC em.txt").text.strip()
                    date = box.select_one("div.cmt_etc em.txt_date").text.strip()
                    self.reviews.append([rating, date, content, sympathy])
                except Exception as e:
                    self.logger.warning(f"리뷰 파싱 실패: {e}")
            
        self.driver.quit()
        self.logger.info(f"총 {len(self.reviews)}개 리뷰 수집 완료")

    def save_to_database(self):
        """
        수집된 리뷰 데이터를 CSV 파일로 저장

        - output_path 위치에 'reviews_yes24.csv' 파일로 저장
        - UTF-8-sig 인코딩으로 한글 호환 보장
        """
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['rating', 'date', 'review', 'sympathy'])
            writer.writerows(self.reviews)
        self.logger.info(f"CSV 저장 완료: {self.output_path}")