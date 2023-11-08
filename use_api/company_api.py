import requests
import json
import os
from datetime import datetime

#company 테이블의 데이터를 전처리하는 스크립트입니다.

# 회사 정보 전처리 함수
def preprocess_company(company_data):
    # 투자금액과 매출이 None이면 바로 None을 반환, 0이면 None으로 처리, 값이 있으면 변환
    investment = company_data.get('funding')
    revenue = company_data.get('revenue')
    
    new_company_data = {
        'id': company_data['id'],
        'name': company_data['name'],
        'num_employees': company_data.get('employeesCount'),
        'investment': None if investment is None or investment == 0 else int(investment * 1000000),
        'revenue': None if revenue is None or revenue == 0 else int(revenue * 1000000),
        'homepage': company_data.get('homeUrl'),
        'loc_info_id': None,
    }
    
    return new_company_data

# API 데이터를 가져오는 클래스 정의
class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder  # 데이터를 저장할 폴더
        self.output_file = os.path.join(self.data_folder, 'company_api.json')  # 파일 경로를 폴더와 함께 설정
        self.all_company_data = []
        self.processed_ids = set()

        # 데이터 폴더가 없으면 생성합니다.
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                job_positions = data['jobPositions']
                
                for job in job_positions:
                    company_id = job['company']['id']
                    if company_id not in self.processed_ids:
                        processed_company = preprocess_company(job['company'])
                        self.all_company_data.append(processed_company)
                        self.processed_ids.add(company_id)
                
                print(f"Processed page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

        self.save_data()

    def save_data(self):
        # 모든 페이지 처리 후 데이터 저장
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(self.all_company_data, file, ensure_ascii=False, indent=4)
            print(f"Data saved to {self.output_file}")

# 메인 실행 구문
if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71  # 예시로 3 페이지까지만 설정
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
