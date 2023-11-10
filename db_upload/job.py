import requests
import pyodbc
import datetime
import re
from config import *

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
        self.numeric_id = 0
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

    def get_location_info_id(self, location_info_id):
        try:
            query = "SELECT id FROM location_info WHERE id = ?"
            self.cursor.execute(query, (location_info_id,))
            result = self.cursor.fetchone()

            if result is not None:
                return location_info_id
            else:
                return None
        except Exception as e:
            print(f"location_info_id 확인 중 오류가 발생했습니다.: {e}")
            return None

    def upload_job_data(self, job_data):
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            location_info_id = self.get_location_info_id(job_data['loc_info_id'])

            insert_query = '''
            INSERT INTO job (id, name, company_id, work_type, due_datetime, min_wage, max_wage, min_experience, max_experience, loc_info_id, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            values = (
                job_data['id'],
                job_data['name'],
                job_data['company_id'],
                job_data['work_type'],
                job_data['due_datetime'],
                job_data.get('min_wage'),
                job_data.get('max_wage'),
                job_data['min_experience'],
                job_data['max_experience'],
                location_info_id,
                now,
                now
            )
            self.cursor.execute(insert_query, values)
            self.conn.commit()
        except Exception as e:
            print(f" ID {job_data['id']} 추가 중 오류가 발생했습니다.: {e}")

    def extract_second_date(self, period_string):
        match = re.search(r'부터 (\d{4}-\d{2}-\d{2} \d{2}:\d{2})까지', period_string)

        if match:
            second_date = match.group(1)
            return second_date
        else:
            return None

    def preprocess_job_data(self, job_data):
        career_range = job_data.get('careerRange')
        if career_range == '신입 채용':
            min_experience = 0
            max_experience = 0
        elif career_range == '경력 무관':
            min_experience = 0
            max_experience = 99
        elif career_range:
            career_range = career_range.split('...')
            min_experience = int(career_range[0])
            max_experience = int(career_range[1]) if len(career_range) > 1 else 99
        else:
            min_experience = 0
            max_experience = 99

        min_wage = job_data.get('minSalary')
        if min_wage is not None:
            min_wage *= 10000
        max_wage = job_data.get('maxSalary')
        if max_wage is not None:
            max_wage *= 10000

        period_string = job_data['period']

        if period_string == '상시 채용':
            second_date = '2999-12-31T23:59:59'
        else:
            second_date = self.extract_second_date(period_string)

        new_job_data = {
            'id': job_data['id'],
            'name': job_data['title'],
            'company_id': job_data['companyId'],
            'work_type': job_data['jobType'],
            'due_datetime': second_date,
            'min_wage': min_wage,
            'max_wage': max_wage,
            'min_experience': min_experience,
            'max_experience': max_experience,
            'loc_info_id': job_data['companyId'],
        }

        return new_job_data

    def preprocess_and_upload_data(self, job_data):
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            location_info_id = self.get_location_info_id(job_data['loc_info_id'])

            insert_query = '''
            INSERT INTO job (id, name, company_id, work_type, due_datetime, min_wage, max_wage, min_experience, max_experience, loc_info_id, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            values = (
                job_data['id'],
                job_data['name'],
                job_data['company_id'],
                job_data['work_type'],
                job_data['due_datetime'],
                job_data.get('min_wage'),
                job_data.get('max_wage'),
                job_data['min_experience'],
                job_data['max_experience'],
                location_info_id,
                now,
                now
            )
            self.cursor.execute(insert_query, values)
            self.conn.commit()
        except Exception as e:
            print(f" ID {job_data['id']} 추가 중 오류가 발생했습니다.: {e}")

    def process_job_data_pages(self):
        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions'][:22]:
                    company_info = job.get('company')
                    if company_info:
                        company_address = company_info.get('address', '').strip() if company_info.get('address') else ''
                        processed_job_data = self.preprocess_job_data(job)
                        try:
                            self.preprocess_and_upload_data(processed_job_data)
                            print(f"페이지 {page} 처리 완료.")
                        except pyodbc.IntegrityError as e:
                            print(f"페이지 {page} 처리 중 오류 발생: {e}")
            else:
                print(f"페이지 {page} 처리 실패, 상태 코드: {job_data.status_code}")
                break

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)

    fetcher.process_job_data_pages()

    print("모든 직무 데이터가 데이터베이스에 업로드되었습니다.")
