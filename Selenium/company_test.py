import pyodbc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import user_agent

# DB 접속 정보
server = 'de-2-111-db.database.windows.net'
database = 'de-2-111'
username = 'dbadmin'
password = 'pa$$w0rd'
driver = '{ODBC Driver 18 for SQL Server}'

# DB 연결 함수
def open_connection():
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;'
    try:
        conn = pyodbc.connect(connection_string)
        print("Connection successful")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# 데이터 삽입 함수
def insert_company_data(conn, data):
    cursor = conn.cursor()
    query = """INSERT INTO company (id, name) VALUES (?, ?);"""
    try:
        cursor.execute(query, (data['id'], data['company_name']))
        conn.commit()
        print(f"Inserted company data: {data}")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()

class Scrape:
    def __init__(self, url, conn):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={user_agent}")
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.url = url
        self.conn = conn  # DB 연결

    def scrape_page(self, idx):
        data = {'id': None, 'company_name': None}
        try:
            self.driver.get(self.url)
            wait = WebDriverWait(self.driver, 20)
            button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="tab_position"]/section/ul/li[{idx}]/a')))
            ActionChains(self.driver).click(button).perform()
            current_url = self.driver.current_url
            company_id = current_url.split('/')[-1]

            data['id'] = int(company_id)
            data['company_name'] = self.scrape_company_name(wait)

            insert_company_data(self.conn, data)  # 데이터베이스에 데이터 삽입

        except Exception as e:
            print(f"Error scraping page index {idx}: {e}")

        finally:
            self.driver.back()
    
    def scrape_company_name(self, wait):
        element_company_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="career-app-legacy"]/div/div/header/div[1]/h1')))
        return element_company_name.text

if __name__ == "__main__":
    url_template = "https://career.programmers.co.kr/companies?page={}"

    conn = open_connection()
    if conn is not None:
        try:
            for page_number in range(1, 2):
                scrape = Scrape(url_template.format(page_number), conn)
                for idx in range(1, 5):
                    scrape.scrape_page(idx)
        except KeyboardInterrupt:
            print("\nScraping was interrupted by user.")
        finally:
            conn.close()
            scrape.driver.quit()
            print("Database connection closed and browser closed.")
