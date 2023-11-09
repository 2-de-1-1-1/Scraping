import requests
import pyodbc
import os
from config import *
import datetime
#job_position_mapping 테이블에 데이터를 전처리하는 스크립트입니다.

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
                    print(f"Fetched data from page {page}")
                else:
                    print(f"The 'jobPositions' key is missing in the response from page {page}.")
                    break
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break
    
    def upload_position_mapping_data(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unique_id = 1
        insert_query = '''
        INSERT INTO job_position_mapping (id, job_id, position_id, created_at, modified_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        for data in self.filtered_data:
            # 여기서 id 값을 생성하거나 가져와야 함
            values = (
                unique_id,
                data["job_id"],
                data["position_id"],
                now,
                now
            )
            try:
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                unique_id += 1
            except Exception as e:
                print(f"Error inserting data: {e}")
                self.conn.rollback()

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
    fetcher.upload_position_mapping_data()
