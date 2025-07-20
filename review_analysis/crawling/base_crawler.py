from abc import ABC, abstractmethod
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver

######## 수정 금지 #########
class BaseCrawler(ABC):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    @abstractmethod
    def start_browser(self):
        pass

    @abstractmethod
    def scrape_reviews(self):
        pass

    @abstractmethod
    def save_to_database(self):
        pass
############################

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from utils.logger import setup_logger
from typing import List
import time
import os
import re

class KyoboCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://product.kyobobook.co.kr/detail/S000000610612'
        self.logger = setup_logger('kyobo.log')
        self.reviews: List[list[str | float]] = []

    def start_browser(self) -> None:
        
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.logger.info("브라우저 실행 완료")

    def scrape_reviews(self):

        self.start_browser()

        self.driver.get(self.base_url)
        try:
            self.driver.maximize_window()
        except:
            pass
        time.sleep(1)

        review_section = self.driver.find_element(By.ID, "scrollSpyProdReview")
        self.driver.execute_script("arguments[0].scrollIntoView();", review_section)
        self.logger.info("리뷰 섹션 스크롤 완료")
        time.sleep(1)

        def remove_emoji(text: str) -> str:
            emoji_pattern = re.compile(
                "["
                "\U00010000-\U0010FFFF"
                "]+",
                flags=re.UNICODE,
            )
            return emoji_pattern.sub(r'', text) 

        page = 1
        while True:

            if page % 10 == 0:
                self.logger.info(f"{page}페이지 리뷰 수집 중...")
            review_items = self.driver.find_elements(By.CLASS_NAME, "comment_item")

            for item in review_items:
                try:
                    # reviwe
                    review = item.find_element(By.CLASS_NAME, "comment_text").text
                    review = remove_emoji(review)
                    
                    # rating
                    style = item.find_element(By.CLASS_NAME, "filled-stars").get_attribute("style")
                    percent = int(style.split(":")[1].replace("%;", "").strip())
                    rating = round(percent / 25)

                    # date
                    info_items = item.find_elements(By.CLASS_NAME, "info_item")
                    date = next(
                        (span.text for span in info_items if "." in span.text and len(span.text.strip()) == 10),
                        "날짜없음"
                    )

                    self.reviews.append([review, rating, date])

                except Exception as e:
                    self.logger.warning(f"{page}페이지에서 리뷰 추출 실패: {e}")

            # 다음 페이지
            try:
                wait = WebDriverWait(self.driver, 10)

                try:
                    blocker = self.driver.find_element(By.CLASS_NAME, "right_area")
                    self.driver.execute_script("arguments[0].style.display='none';", blocker)
                except:
                    pass 

                next_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_page.next")))

                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.3)

                if next_button.get_attribute("disabled") is not None:
                    self.logger.info("마지막 페이지 도달")
                    break

                self.driver.execute_script("arguments[0].click();", next_button)
                page += 1
                time.sleep(1)

            except Exception as e:
                self.logger.warning(f"페이지 넘기기 실패: {e}")
                break

    def save_to_database(self):

        file_path = os.path.join(self.output_dir, 'reviews_kyobo.csv')

        df = pd.DataFrame(self.reviews, columns=["review", "rating", "date"])
        df.to_csv(file_path, encoding="utf-8-sig", index=False)

        self.logger.info(f"데이터 저장 완료: {file_path}")

        self.driver.quit()


class Yes24Crawler(BaseCrawler):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

class AladinCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir