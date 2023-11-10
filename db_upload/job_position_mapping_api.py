import requests
import pyodbc
import os
from config import *
import datetime

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
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
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
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
                    print(f"{page} 수집 완료")
                else:
                    print(f"{page} job position key가 없습니다.")
                    break
            else:
                print(f" {page} 로드 실패. Status code: {response.status_code}")
                break
    
    def upload_position_mapping_data(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO job_position_mapping (job_id, position_id, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''
        for data in self.filtered_data:
            values = (
                data["job_id"],
                data["position_id"],
                now,
                now
            )
            try:
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                print(f"{data['job_id']}, {data['position_id']} 업로드 완료")
            except Exception as e:
                print(f"{data['job_id']}에서 오류 발생: {e}")
                self.conn.rollback()

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
    fetcher.upload_position_mapping_data()
