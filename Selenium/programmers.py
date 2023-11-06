from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"


class Scrape:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={user_agent}")
        self.chrome_options = chrome_options
        self.url = url
        self.all_data = []

    def scrape_page(self, idx):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.get(self.url)
        #self.driver.maximize_window()
        wait = WebDriverWait(self.driver, 30)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="list-positions-wrapper"]/ul/li[{idx}]')))
        ActionChains(self.driver).click(button).perform()

        data = {}
        data['title'] = self.scrape_title(wait)
        data['company_name'] = self.scrape_company_name(wait)
        data['infomation']  = self.scrape_information(wait)
        data['techstack'] = self.scrape_required_techstack(wait)

        self.all_data.append(data)

        self.driver.back()

        return data
    
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
    try:
        for page_number in range(1,5):
            scrape = Scrape(f"https://career.programmers.co.kr/job?page={page_number}&order=recent")
            
            for idx in range(1,22):
                try :
                    data = scrape.scrape_page(idx)
                    if data:
                        collected_data.append(data)
                except Exception as e:
                    print(f"페이지 {page_number}, 항목{idx}에서 에러 발생: {e}")

    except KeyboardInterrupt:
        print("\n 스크래핑을 강제 중단합니다. json으로 백업합니다.")
        with open('collected_data.json', 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=4)
    
    print(collected_data)


