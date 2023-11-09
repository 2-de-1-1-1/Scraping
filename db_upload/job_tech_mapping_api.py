import requests
from config import *
import pyodbc
import datetime
#job api에서 tech stack을 임시저장한 다음 tech stack의 유니크 값을 만들어 이와 비교해 job과 tech_stack을 매핑하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.unique_technical_tags = {}  # 중복을 방지하기 위해 딕셔너리 사용
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
                        job_tech_dict = {"job_id": job["id"], "tech_id": tag["id"]}
                        self.extracted_data.append(job_tech_dict)
                print(f"페이지 {page}에서 데이터를 가져오고 추출했습니다.")
            else:
                print(f"페이지 {page}에서 데이터를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
                break

    def upload_job_tech_mapping_data(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unique_id = 1
        insert_query = '''
        INSERT INTO job_tech_mapping (id, job_id, tech_id, created_at, modified_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        for data in self.extracted_data:
            values = (
                unique_id,
                data["job_id"],
                data["tech_id"],
                now,
                now
            )
            try:
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                unique_id += 1
            except Exception as e:
                print(f"데이터 삽입 중 오류 발생: tech_id {data['tech_id']} - {e}")
                self.conn.rollback()



if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 8

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data()  # 데이터를 가져와서 유니크한 기술 태그 추출
    fetcher.upload_job_tech_mapping_data()  # 기술 태그 매핑 생성 및 저장
