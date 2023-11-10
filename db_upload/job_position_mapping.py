import requests
import pyodbc
import os
import sys
from config import *
import datetime
from logging_config import *

logger = logging.getLogger(script_name)

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.filtered_data = []  
        self.conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.cursor = self.conn.cursor()

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = self.base_job_url + str(page)  # 기존 코드에서 수정된 부분
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'jobPositions' in data:
                    for job in data['jobPositions']:
                        for category_id in job["jobCategoryIds"]:
                            self.filtered_data.append({
                                "job_id": job["id"],
                                "position_id": category_id
                            })
                    logger.info(f"{page} 수집 완료")
                else:
                    logger.info(f"{page} job position key가 없습니다.")
                    break
            else:
                logger.info(f" {page} 로드 실패. Status code: {response.status_code}")
                break
    
    def upload_position_mapping_data(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO job_position_mapping (job_id, position_id, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''
        for data in self.filtered_data:
            job_id = data["job_id"]
            position_id = data["position_id"]
            
            if not self.job_position_pair_exists(job_id, position_id):
                values = (
                    job_id,
                    position_id,
                    now,
                    now
                )
                try:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"{job_id}, {position_id} 업로드 완료")
                except Exception as e:
                    logger.info(f"{job_id}에서 오류 발생: {e}")
                    self.conn.rollback()
            else:
                logger.info(f"{job_id}, {position_id} 이미 데이터베이스에 존재하여 업로드 건너뛰었습니다.")

    def job_position_pair_exists(self, job_id, position_id):
        query = "SELECT COUNT(*) FROM job_position_mapping WHERE job_id = ? AND position_id = ?"
        self.cursor.execute(query, (job_id, position_id))
        return self.cursor.fetchone()[0] > 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])
    
    fetcher = JobApiFetcher(start_page=start_page, end_page=end_page)
    fetcher.fetch_data()
    fetcher.upload_position_mapping_data()
