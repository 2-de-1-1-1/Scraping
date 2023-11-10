import requests
import pyodbc
import datetime
from config import *  


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
        print(f"페이지 {page} 의 정보를 가져오는 중...")
        response = requests.get(f"{self.base_job_url}{page}")
        return response.json() if response.status_code == 200 else None

    def fetch_company_geo(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            company_data = response.json()['company']
            return {
                'id': company_data.get('id'),
                'address': company_data.get('address', ''),
                'latitude': company_data.get('latitude', None),
                'longitude': company_data.get('longitude', None)
            }
        else:
            return None

    def insert_data_to_db(self, company_data):
        insert_query = '''
            INSERT INTO location_info (id, address, geo_lat, geo_alt, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(insert_query, (
            company_data['id'],
            company_data['address'],
            company_data['latitude'],
            company_data['longitude'],
            now,
            now
        ))
        self.conn.commit()

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            print(f"페이지 {page} 작업 중")
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    company_info = self.fetch_company_geo(company_id)
                    if company_info and company_info['address']:
                        self.insert_data_to_db(company_info)
            print(f"페이지 {page} 작업 완료")
        print("모든 페이지 작업 완료")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
