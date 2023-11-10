import requests
from config import *
import pyodbc
import datetime

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.unique_technical_tags = {} 
        self.extracted_data = []
        self.conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.cursor = self.conn.cursor()


    def fetch_and_extract_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                jobs_data = response.json().get('jobPositions', [])
                for job in jobs_data:
                    for tag in job.get("technicalTags", []):
                        job_tech_dict = {"job_id": job["id"], "tech_id": tag["id"], "tech_name" : tag["name"]}
                        self.extracted_data.append(job_tech_dict)
                print(f"페이지 {page}에서 데이터를 가져오고 추출했습니다.")
            else:
                print(f"페이지 {page}에서 데이터를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
                break

    def upload_job_tech_mapping_data(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO job_tech_mapping (job_id, tech_id, created_at, modified_at)
        VALUES (?, ?, ?, ?)
        '''
        
        processed_tech_job_pairs = set()  

        for data in self.extracted_data:
            tech_id = data["tech_id"]
            job_id = data["job_id"]
            tech_name = data["tech_name"]

            if (job_id, tech_id) in processed_tech_job_pairs:
                continue

            if not self.check_tech_job_pair_exists(job_id, tech_id):
                if not self.insert_new_tech_stack(tech_id, tech_name):
                    self.insert_new_tech_stack(tech_id, tech_name)
            
            values = (
                job_id,
                tech_id,
                now,
                now
            )
            try:
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                print(f"데이터 삽입 완료: job_id {job_id}, tech_id {tech_id}")
                processed_tech_job_pairs.add((job_id, tech_id))

            except Exception as e:
                print(f"데이터 삽입 중 오류 발생: job_id {job_id}, tech_id {tech_id} - {e}")
                self.conn.rollback()

    def check_tech_job_pair_exists(self, job_id, tech_id):
        select_query = '''
        SELECT id FROM job_tech_mapping WHERE job_id = ? AND tech_id = ?
        '''
        self.cursor.execute(select_query, (job_id, tech_id))
        row = self.cursor.fetchone()
        return row is not None
    
    def check_tech_id_exists(self, tech_id):
        select_query = '''
        SELECT id FROM tech_stack WHERE id = ?
        '''
        self.cursor.execute(select_query, (tech_id,))
        row = self.cursor.fetchone()
        return row is not None
    
    def insert_new_tech_stack(self, tech_id, tech_name):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        select_query = '''
        SELECT id FROM tech_stack WHERE id = ?
        '''
        self.cursor.execute(select_query, (tech_id,))
        row = self.cursor.fetchone()
        
        if row is None:
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
                print(f"기술 스택 추가: ID {tech_id}, Name {tech_name}")
                return True

            except Exception as e:
                print(f"기술 스택 추가 중 오류 발생 : ID {tech_id}, Name {tech_name} - {e}")
                self.conn.rollback()

        return False




if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data() 
    fetcher.upload_job_tech_mapping_data()  
