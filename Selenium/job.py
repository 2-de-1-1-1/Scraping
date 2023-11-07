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
            'name': None,
            'company_name': None,
            'work_type': None,
            'due_datetime': None,
            'wage': None,
            'experience': None,
            'loc_info': None,
            'techstack': [],
        }
        
        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 120)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="list-positions-wrapper"]/ul/li[{idx}]')))
            ActionChains(self.driver).click(button).perform()

            current_url = self.driver.current_url
            job_id = current_url.split('/')[-1]
            data['id'] = int(job_id) 

            data['name'] = self.scrape_title(wait)
            data['company_name'] = self.scrape_company_name(wait)
            information = self.scrape_information(wait)
            data.update(self.transform_information(information))
            data['techstack'] = self.scrape_required_techstack(wait)

        except Exception as e:
            error_msg = f"항목 {idx} 에서 에러 발생: {str(e)}"
            print(error_msg)

        finally:
            self.all_data.append(data) 
            self.driver.back()
            return data
    
    def transform_information(self, info_dict):
        new_info = {
            'name': info_dict.get('직무'),
            'work_type': info_dict.get('고용 형태'),
            'due_datetime': info_dict.get('지원 마감'),
            'wage': info_dict.get('연봉'),
            'experience': info_dict.get('경력'),
            'loc_info' : info_dict.get('근무 위치'),

        }
        return new_info
    
    def scrape_title(self, wait):
        element_title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/header/div/div[2]/div/h2')))
        title = element_title.text
        return title

    def scrape_company_name(self, wait):
        element_company_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/header/div/div[2]/h4/a')))
        company_name = element_company_name.text
        return company_name

    def scrape_information(self, wait):
        element_infomation = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/section/div')))
        info = element_infomation.text
        info_list = [item.strip() for item in info.split("\n") if item]
        info_dict = dict(zip(info_list[::2], info_list[1::2]))
        return info_dict

    def scrape_required_techstack(self, wait):
        element_techstack = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/div[2]/section/ul')))
        techstack_list = element_techstack.text
        return techstack_list.split('\n')

    
if __name__ == "__main__":
    collected_data = []
    error_messages = []
    completed_successfully = False

    save_dir = 'job_data'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    try:
        for page_number in range(1, 3):
            scrape = Scrape(f"https://career.programmers.co.kr/job?page={page_number}&order=recent")
            for idx in range(1, 4):
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
        data_filename = os.path.join(save_dir, f"collected_job_data_{timestamp}_{'completed' if completed_successfully else 'interrupted'}.json")
        error_filename = os.path.join(save_dir, f"job_error_log_{timestamp}.json")

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


