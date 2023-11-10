import requests
from config import *
import pyodbc
import datetime

#company_welfare_mapping 테이블의 정보를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
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
            print(f"페이지 {page}에서 직무 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_welfare(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            data = response.json()
            return data['company'].get('benefitTags', [])
        else:
            print(f"회사 ID {company_id}에 대한 welfare를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return []

    def fetch_data(self):
        all_benefit_data = []

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    benefits = self.fetch_company_welfare(company_id)
                    if benefits is not None:
                        for benefit in benefits:
                            all_benefit_data.append({
                                'company_id': company_id,
                                'welfare_name': benefit
                            })
            
            print(f"{page}페이지 진행중")
        
        return all_benefit_data
    
    def welfare_name_exists(self, welfare_name):
        check_query = "SELECT COUNT(*) FROM welfare WHERE name = ?"
        self.cursor.execute(check_query, (welfare_name,))
        return self.cursor.fetchone()[0] > 0

    def upload_welfare_data(self, all_benefit_data):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO welfare (name, created_at, modified_at)
        VALUES (?, ?, ?)
        '''

        for data in all_benefit_data:
            company_id = data["company_id"]
            welfare_name = data["welfare_name"]
            if not self.welfare_name_exists(welfare_name):
                values = (
                    data["welfare_name"],
                    now,
                    now
                )
                try:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    print(f"{data['welfare_name']} welfare에 업로드")
                except Exception as e:
                    print(f"welfare 데이터 삽입 중 오류 발생 : name {data['welfare_name']} - {e}")
                    self.conn.rollback()


    def get_welfare_id(self, welfare_name):
        query = "SELECT id FROM welfare WHERE name = ?"
        self.cursor.execute(query, (welfare_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None


    def upload_company_welfare_mapping_data(self, all_benefit_data):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO company_welfare_mapping (company_id, welfare_id, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''

        for data in all_benefit_data:
            company_id = data["company_id"]
            welfare_name = data["welfare_name"]
            welfare_id = self.get_welfare_id(welfare_name)
            if welfare_id:
                values = (
                    data["company_id"],
                    welfare_id,
                    now,
                    now
                )
                try:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    print(f"{data['welfare_name']} company_welfare_mapping 업로드")
                except Exception as e:
                    print(f"company_welfare_mapping 삽입 중 오류 발생 : name {data['welfare_name']} - {e}")
                    self.conn.rollback()

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71


    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    all_benefit_data = fetcher.fetch_data()
    fetcher.upload_welfare_data(all_benefit_data)
    fetcher.upload_company_welfare_mapping_data(all_benefit_data)