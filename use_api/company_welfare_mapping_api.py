import requests
import json
import os

#company_welfare_mapping 테이블의 정보를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder
        self.company_welfare_file_path = os.path.join(self.data_folder, 'company_welfare_mapping_api.json')
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.benefit_id_map = {}  
        self.benefit_counter = 1


        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"페이지 {page}에서 직무 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_benefits(self, company_id):
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            company_data = response.json()
            return company_data['company'].get('benefitTags', [])
        else:
            print(f"회사 ID {company_id}에 대한 복리후생 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return []

    def generate_unique_benefits_and_mapping(self):
        company_benefit_relations = [] 
        mapping_id = 1

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    benefits = self.fetch_company_benefits(company_id)
                    for benefit in benefits:
                        if benefit not in self.benefit_id_map:
                            self.benefit_id_map[benefit] = self.benefit_counter
                            self.benefit_counter += 1
                        company_benefit_relations.append({
                            "id": mapping_id,
                            "company_id": company_id,
                            "welfare_id": self.benefit_id_map[benefit]
                        })
                        mapping_id += 1

        with open(self.company_welfare_file_path, 'w', encoding='utf-8') as company_welfare_file:
            json.dump(company_benefit_relations, company_welfare_file, ensure_ascii=False, indent=4)
        
        print(f"회사와 복지 혜택 관계 데이터를 {self.company_welfare_file_path}에 저장했습니다.")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71 
    data_folder = 'api_data'

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder)
    fetcher.generate_unique_benefits_and_mapping()
