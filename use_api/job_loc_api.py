import requests
import json
import os

# JobApiFetcher 클래스 정의
class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data', output_file='loc_info.json'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder
        self.output_file = os.path.join(self.data_folder, output_file)
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
        self.numeric_id = 0

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            print(f"페이지 {page}: 직무 정보를 성공적으로 가져왔습니다.")
            return response.json()
        else:
            print(f"페이지 {page}: 직무 정보 가져오기 실패. 상태 코드: {response.status_code}")
            return None

    def fetch_company_geo(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            data = response.json()
            
            # 'company' 키가 있는지 확인하고, 그 값을 company_data에 할당합니다.
            company_data = data.get('company')
            if not company_data:  # company_data가 None이면 다음 회사로 넘어갑니다.
                return None

            # company_data가 유효한 경우, 'address' 키의 값을 가져와서 strip 메서드를 호출합니다.
            address = company_data.get('address', '')
            if address:  # address가 비어 있지 않은 문자열이면 strip 메서드를 호출합니다.
                address = address.strip()
                if address:  # 주소가 비어 있지 않은 경우
                    self.numeric_id += 1
                    return {
                        'id': self.numeric_id,
                        'address': address,
                        'latitude': company_data.get('latitude', None),
                        'longitude': company_data.get('longitude', None)
                    }
        else:
            print(f"회사 ID {company_id}: 회사 정보 가져오기 실패. 상태 코드: {response.status_code}")
        return None



    def fetch_and_save_loc_info(self):
        loc_info_data = []

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    loc_info = self.fetch_company_geo(company_id)
                    if loc_info:
                        loc_info_data.append(loc_info)

        return {info['address']: info['id'] for info in loc_info_data}

# 함수를 정의하여 직무 정보를 전처리합니다.
def preprocess_job_data(job_data, loc_info_id):
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
        'loc_info_id': loc_info_id,
    }
    
    return new_job_data


# 메인 실행 로직
if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    data_folder = 'api_data'  # 데이터를 저장할 폴더 이름

    # JobApiFetcher 인스턴스 생성 및 주소-ID 매핑 데이터 수집
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder)
    address_to_id_map = fetcher.fetch_and_save_loc_info()

    all_job_data = []  # 전처리된 모든 직무 데이터를 저장할 리스트

    # 직무 데이터를 페이지 별로 가져오고 전처리합니다.
    for page in range(start_page_index, end_page_index + 1):
        url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            for job_data in data['jobPositions']:
                # company 정보를 안전하게 접근합니다.
                company_info = job_data.get('company')
                if company_info:
                    # address 정보를 안전하게 접근하고, strip()을 호출합니다.
                    company_address = company_info.get('address', '').strip() if company_info.get('address') else ''
                    # loc_info_id를 매핑합니다.
                    loc_info_id = address_to_id_map.get(company_address) if company_address else None
                    processed_job_data = preprocess_job_data(job_data, loc_info_id)
                    all_job_data.append(processed_job_data)
            print(f"페이지 {page} 처리 완료.")
        else:
            print(f"페이지 {page} 처리 실패, 상태 코드: {response.status_code}")
            break

    # 전처리된 직무 데이터를 JSON 파일로 저장합니다.
    jobs_output_file = os.path.join(data_folder, 'job_loc_api.json')
    with open(jobs_output_file, 'w', encoding='utf-8') as file:
        json.dump(all_job_data, file, ensure_ascii=False, indent=4)
    print(f"전처리된 직무 데이터가 {jobs_output_file}에 저장되었습니다.")
