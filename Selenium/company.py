from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from config import *
import json
import datetime
import os

class Scrape:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={user_agent}")
        #service = Service(chrome_driver_path)
        #self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.url = url
        self.all_data = []

    def scrape_page(self, idx):
        data = {
            'id': None,
            'company_name': None,
            'company_info': None,
            'company_welfare': None,
        }

        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 20)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="tab_position"]/section/ul/li[{idx}]/a')))
            ActionChains(self.driver).click(button).perform()
            current_url = self.driver.current_url
            company_id = current_url.split('/')[-1]

            data['id'] = int(company_id)
            data['company_name'] = self.scrape_company_name(wait)
            data['company_info'] = self.scrape_company_info(wait)
            data['company_welfare'] = self.scrape_company_welfare(wait)

        except Exception as e:
            print(f"항목 {idx}에서 에러 발생: {e}")

        finally:
            self.all_data.append(data)
            self.driver.back()
            return data
    
    def scrape_company_name(self, wait):
        element_company_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div/div/header/div[1]/h1')))
        title = element_company_name.text
        return title
    
    def scrape_company_info(self, wait):
        elements_company_info = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="career-app-legacy"]/div/div/div/div[2]/section[1]/ul/li')))
        company_info = [element.text.replace('\n', ' : ') for element in elements_company_info]
        return company_info
    
    def scrape_company_welfare(self, wait):
        elements_company_welfare = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="career-app-legacy"]/div/div/div/div[2]/section[2]/ul/li')))
        company_welfare = [element.text for element in elements_company_welfare]
        return company_welfare

    
if __name__ == "__main__":
    collected_data = []
    error_messages = []
    completed_successfully = False

    save_dir = 'company_data'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    try:
        for page_number in range(1, 3):
            scrape = Scrape(f"https://career.programmers.co.kr/companies?page={page_number}")            
            for idx in range(1, 18):
                try:
                    data = scrape.scrape_page(idx)
                    job_id = data.get('id', None)
                    if data:
                        collected_data.append(data)
                except Exception as e:
                    error_msg = f"페이지 {page_number}, 항목 {idx} 에서 에러 발생: {str(e)}"
                    print(error_msg)
                    error_messages.append(error_msg)

        completed_successfully = True

    except KeyboardInterrupt:
        print("\n스크래핑을 사용자에 의해 강제 중단합니다.")
        error_messages.append("스크래핑이 사용자에 의해 강제로 중단되었습니다.")

    finally:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        data_filename = os.path.join(save_dir, f"company_collected_data_{timestamp}_{'completed' if completed_successfully else 'interrupted'}.json")
        error_filename = os.path.join(save_dir, f"company_error_log_{timestamp}.json")

        # 스크랩 데이터 저장
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=4)

        # 에러 로그 저장
        if error_messages:
            with open(error_filename, 'w', encoding='utf-8') as f:
                json.dump(error_messages, f, ensure_ascii=False, indent=4)

        print(f"\n스크래핑 결과를 '{data_filename}' 파일로 저장했습니다.")
        if error_messages:
            print(f"오류 로그를 '{error_filename}' 파일로 저장했습니다.")

#테스트

