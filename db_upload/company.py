import requests
import os
import pyodbc
from config import *
import datetime

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.cursor = self.conn.cursor()

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            print(f"페이지 {page}: 직무 정보를 성공적으로 가져왔습니다.")
            return response.json()
        else:
            print(f"페이지 {page}: 직무 정보 가져오기 실패. 상태 코드: {response.status_code}")
            return None

    def check_company_exists(self, company_id):
        self.cursor.execute("SELECT COUNT(1) FROM Company WHERE id=?", company_id)
        return self.cursor.fetchone()[0] > 0

    def upload_company_data(self, company_data):
        try:
            if not self.check_company_exists(company_data['id']):
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간
                insert_query = '''
                INSERT INTO Company (id, name, num_employees, investment, revenue, homepage, loc_info_id, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                values = (
                    company_data['id'],
                    company_data['name'],
                    company_data.get('num_employees'),
                    company_data.get('investment'),
                    company_data.get('revenue'),
                    company_data.get('homepage'),
                    company_data.get('loc_info_id'),
                    now,
                    now
                )
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                print(f"기업 ID {company_data['id']}가 데이터베이스에 추가되었습니다.")
            else:
                print(f"기업 ID {company_data['id']}는 이미 데이터베이스에 존재합니다.")
        except Exception as e:
            print(f"기업 ID {company_data['id']} 추가 중 오류가 발생했습니다: {e}")

def preprocess_company(company_data):
    investment = company_data.get('funding')
    revenue = company_data.get('revenue')
    address = company_data.get('address')
    
    new_company_data = {
        'id': company_data['id'],
        'name': company_data['name'],
        'num_employees': company_data.get('employeesCount'),
        'investment': None if investment is None or investment == 0 else int(investment * 1000000),
        'revenue': None if revenue is None or revenue == 0 else int(revenue * 1000000),
        'homepage': company_data.get('homeUrl'),
        'loc_info_id': None if not address else company_data['id'],
    }
    
    return new_company_data

def fetch_and_upload_companies(fetcher, start_page, end_page):
    processed_companies = set()
    for page in range(start_page, end_page + 1):
        url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            for job_data in data['jobPositions'][:22]:
                company_info = job_data.get('company')
                if company_info:
                    company_id = company_info['id']
                    if company_id not in processed_companies:
                        processed_companies.add(company_id)
                        processed_company_data = preprocess_company(company_info)
                        fetcher.upload_company_data(processed_company_data)  # 업로드
            print(f"페이지 {page} 처리 완료.")
        else:
            print(f"페이지 {page} 처리 실패, 상태 코드: {response.status_code}")
            break

    print("모든 기업 데이터가 서버 데이터베이스에 업로드되었습니다.")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 2

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetch_and_upload_companies(fetcher, start_page_index, end_page_index)
