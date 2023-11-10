import requests
from config import *
import pyodbc
import datetime
import sys
from logging_config import *

logger = logging.getLogger(script_name)

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
            logger.info(f"{page}로드 실패. Status code: {response.status_code}")
            return None

    def fetch_company_details(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            data = response.json()
            technical_tags = [
                {'company_id': company_id, 'tech_id': tag['id'], 'name' : tag['name']}
                for tag in data['company'].get('technicalTags', [])
            ]
            return technical_tags
        else:
            logger.info(f" {company_id}기술 태그 수집 실패. Status code: {response.status_code}")
            return []

    def fetch_data(self):
        all_technical_data = []

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    technical_tags = self.fetch_company_details(company_id)
                    if technical_tags:
                        all_technical_data.extend(technical_tags)
            
            logger.info(f"{page}페이지 진행중")
        
        return all_technical_data
    
    def check_tech_id_exists(self, tech_id):
        select_query = '''
        SELECT id FROM tech_stack WHERE id = ?
        '''
        self.cursor.execute(select_query, (tech_id,))
        row = self.cursor.fetchone()
        return row is not None

    def insert_new_tech_stack(self, tech_id, tech_name):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO tech_stack (id, name, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''

        values = (
            tech_id,
            tech_name,
            now,
            now
        )
        
        try:
            self.cursor.execute(insert_query, values)
            self.conn.commit()
            logger.info(f"기술 스택 추가: ID {tech_id}, Name {tech_name}")
        except Exception as e:
            logger.info(f"기술 스택 추가 중 오류 발생 : ID {tech_id}, Name {tech_name} - {e}")
            self.conn.rollback()

    def check_duplicate_data(self, company_id, tech_id):
        select_query = '''
        SELECT * FROM company_tech_mapping WHERE tech_id = ? AND company_id = ?
        '''
        self.cursor.execute(select_query, (company_id, tech_id))
        row = self.cursor.fetchone()
        return row is not None

    def upload_compnay_tech_data(self, all_technical_data):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO company_tech_mapping (company_id, tech_id, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''

        for data in all_technical_data:
            tech_id = data["tech_id"]
            tech_name = data["name"]
            company_id = data["company_id"]

            # 중복 데이터 확인
            if self.check_duplicate_data(tech_id, company_id):
                logger.info(f"중복 데이터로 처리됨: company_id {company_id}, tech_id {tech_id}")
                continue

            # tech_stack 테이블에 기술 스택 추가 (없을 경우)
            if not self.check_tech_id_exists(tech_id):
                self.insert_new_tech_stack(tech_id, tech_name)

            values = (
                company_id,
                tech_id,
                now,
                now
            )
            try:
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                logger.info(f"데이터 삽입 완료: company_id {company_id}, tech_id {tech_id}")
            except Exception as e:
                logger.info(f"데이터 삽입 중 오류 발생 : tech_id {tech_id} - {e}")
                self.conn.rollback()



if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])


    fetcher = JobApiFetcher(start_page=start_page, end_page=end_page)
    all_technical_data = fetcher.fetch_data()
    fetcher.upload_compnay_tech_data(all_technical_data)
