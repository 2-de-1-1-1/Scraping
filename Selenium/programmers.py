from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import time

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"


class Scrape:
    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument(f"user-agent={user_agent}")
        self.chrome_options = chrome_options
        self.url = url
        self.all_data = []

    def scrape_page(self, idx):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(1)
        button = self.driver.find_element(By.XPATH, f'//*[@id="list-positions-wrapper"]/ul/li[{idx}]')
        ActionChains(self.driver).click(button).perform()
        time.sleep(5)

        data = {}
        data['title'] = self.scrape_title()
        data['company_name'] = self.scrape_company_name()
        data['infomation']  = self.scrape_information()
        data['techstack'] = self.scrape_required_techstack()

        self.all_data.append(data)

        self.driver.back()
        time.sleep(3)
    
    def scrape_title(self):
        element_title = self.driver.find_element(By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/header/div/div[2]/div/h2')
        title = element_title.text
        return title

    def scrape_company_name(self):
        element_company_name = self.driver.find_element(By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/header/div/div[2]/h4/a')
        company_name = element_company_name.text
        return company_name

    def scrape_information(self):
        element_infomation = self.driver.find_element(By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/section/div')
        info = element_infomation.text
        info_list = [item.strip() for item in info.split("\n") if item]
        info_dict = dict(zip(info_list[::2], info_list[1:2]))
        return info_dict

    def scrape_required_techstack(self):
        element_techstack = self.driver.find_element(By.XPATH, '//*[@id="career-app-legacy"]/div[1]/div[1]/div[1]/div[2]/section/ul')
        techstack_list = element_techstack.text
        return techstack_list.split('\n')

    
if __name__ == "__main__":
    scrape = Scrape("https://career.programmers.co.kr/job?page=1&order=recent")
    for idx in range(1,5):
        scrape.scrape_page(idx)
    
    print(scrape.all_data)


