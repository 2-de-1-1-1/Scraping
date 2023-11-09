import requests
import json
import os

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data', output_file='benefit_data.json'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder  # 데이터를 저장할 폴더
        self.output_file = os.path.join(self.data_folder, output_file)  # 최종 JSON 파일의 경로
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()  # 이미 조회한 회사 ID를 기록
        self.numeric_id = 0

        # 데이터 폴더가 없으면 생성
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_job_positions(self, page):
        # 직무 정보를 페이지별로 가져오는 함수
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"페이지 {page}에서 직무 정보를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_geo(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id) 
            data = response.json()
            company_data = data['company']
            return {
                'address': company_data.get('address', ''),
                'latitude': company_data.get('latitude', None),
                'longitude': company_data.get('longitude', None)
            }
        else:
            print(f"회사 ID {company_id}에 대한 정보를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
            return {}

    def fetch_data(self):
        # 모든 데이터를 가져와 파일로 저장하는 함수
        all_company_data = []

        print(f"데이터 수집을 시작합니다. 페이지 {self.start_page}부터 {self.end_page}까지 진행합니다.")
        for page in range(self.start_page, self.end_page + 1):
            print(f"페이지 {page} 처리 중...")
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    company_info = self.fetch_company_geo(company_id)
                    if company_info and company_info['address']: 
                        self.numeric_id += 1 
                        all_company_data.append({
                            'id' : self.numeric_id,
                            'address': company_info['address'],
                            'geo_lat': company_info['latitude'],
                            'geo_alt': company_info['longitude']
                        })
                print(f"페이지 {page} 처리 완료.")
            else:
                print(f"페이지 {page} 처리를 실패했습니다.")

        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(all_company_data, file, ensure_ascii=False, indent=4)
        
        print(f"모든 데이터를 {self.output_file}에 저장했습니다.")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    data_folder = 'api_data'  # 데이터 폴더 이름
    output_file = 'location_info_api.json'  # 출력 파일 이름

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder, output_file=output_file)
    fetcher.fetch_data()  # 데이터 수집 시작
