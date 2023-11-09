import requests
import pyodbc
from config import * 
import datetime

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
        self.next_id = 1
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
            return response.json()
        else:
            print(f"페이지 {page}에서 직무 정보를 가져오지 못했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_benefits(self, company_id):
        if company_id in self.companies_seen:
            return None
        self.companies_seen.add(company_id)
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            company_data = response.json()
            return company_data['company'].get('benefitTags', [])
        else:
            print(f"회사 ID {company_id}에 대한 혜택 정보를 가져오지 못했습니다. 상태 코드: {response.status_code}")
            return []

    def fetch_and_insert_unique_benefits_to_db(self):
        print(f"복지 혜택 데이터를 수집하여 데이터베이스에 삽입합니다. 대상 페이지 범위: {self.start_page} ~ {self.end_page}")

        for page in range(self.start_page, self.end_page + 1):
            print(f"{page}페이지의 직무 정보를 수집 중입니다...")
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions'][:22]:
                    company_id = job['companyId']
                    benefits = self.fetch_company_benefits(company_id)
                    if benefits:
                        for benefit in benefits:
                            if not self.check_existing_benefit(benefit):
                                self.insert_data_to_db(benefit)

            print(f"{page}페이지 처리 완료.")
    
    def check_existing_benefit(self, benefit):
        # 이미 데이터베이스에 있는 혜택인지 확인합니다.
        query = 'SELECT COUNT(*) FROM welfare WHERE name = ?'
        self.cursor.execute(query, (benefit,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def insert_data_to_db(self, benefit):
        insert_query = '''
            INSERT INTO welfare (id, name, created_at, modified_at)
            VALUES (?, ?, ?, ?)
        '''
        current_time = datetime.datetime.now()
        
        # 혜택을 데이터베이스에 삽입
        self.cursor.execute(insert_query, (
            self.next_id,
            benefit,
            current_time,
            current_time
        ))
        
        self.next_id += 1  # 다음 ID를 증가
        self.conn.commit()  # 변경 사항 커밋

        print(f"데이터베이스에 혜택 '{benefit}' 데이터를 성공적으로 삽입했습니다.")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71

    # JobApiFetcher 인스턴스 생성 및 데이터 수집 및 데이터베이스 삽입
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_insert_unique_benefits_to_db()
