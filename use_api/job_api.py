import requests
import json
import os

#job 테이블에 맞게 job api를 전처리하는 스크립트입니다.

# 전처리 함수 정의
def preprocess_json(job_data):
    career_range = job_data.get('careerRange')
    if career_range == '신입 채용':
        min_experience = 0
        max_experience = 0
    elif career_range == '경력 무관':
        min_experience = 0
        max_experience = 99
    elif career_range:  # careerRange가 None이 아닌 문자열일 경우
        # "2...7"과 같은 문자열을 처리할 수 있도록 '...'을 구분자로 사용
        career_range = career_range.split('...')
        min_experience = int(career_range[0])
        # 최대 경력이 명시되지 않았을 경우 99로 설정
        max_experience = int(career_range[1]) if len(career_range) > 1 else 99
    else:
        # careerRange가 None이거나 예상치 못한 값일 경우
        min_experience = 0
        max_experience = 99

    # minSalary와 maxSalary에 대한 처리를 None 검사 후에 수행
    min_wage = job_data.get('minSalary')
    if min_wage is not None:
        min_wage *= 10000
    max_wage = job_data.get('maxSalary')
    if max_wage is not None:
        max_wage *= 10000

    # 변환된 데이터를 새로운 딕셔너리에 할당
    new_job_data = {
        'id': job_data['id'],
        'name': job_data['title'],
        'company_id': job_data['companyId'],
        'work_type': job_data['jobType'],
        'due_datetime': '2999-12-31T23:59:59+09:00' if job_data['period'] == '상시 채용' else job_data['startAt'],
        'min_wage': min_wage,
        'max_wage': max_wage,
        'min_experience': min_experience,
        'max_experience': max_experience,
        'loc_info_id': None,
    }
    
    return new_job_data

# API 데이터를 가져오는 클래스 정의
class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder  # 데이터를 저장할 폴더
        self.all_data = []  # 전처리된 모든 데이터를 저장하는 리스트

        # 데이터 폴더가 없으면 생성
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                job_positions = data['jobPositions']
                
                # 페이지별로 가져온 데이터를 전처리하고 리스트에 추가
                for job in job_positions:
                    self.all_data.append(preprocess_json(job))
                
                print(f"Processed page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

    def save_data(self):
        file_path = os.path.join(self.data_folder, 'job_api.json')  # 파일 경로 설정
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.all_data, file, ensure_ascii=False, indent=4)
            print(f"Data saved to {file_path}")

# 메인 실행 구문
if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
    fetcher.save_data()
