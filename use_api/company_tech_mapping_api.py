import requests
import json
import os

#company_tech_mapping 테이블의 정보를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder
        self.company_tech_stack_file_path = os.path.join(self.data_folder, 'company_tech_stack_mapping_api.json')
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"


        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_job_positions(self, page):
        response = requests.get(f"{self.base_job_url}{page}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"{page} 페이지의 직무 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_technical_tags(self, company_id):
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            company_data = response.json()
            return company_data['company'].get('technicalTags', [])
        else:
            print(f"회사 ID {company_id}의 기술 태그를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return []

    def generate_unique_tech_stacks_and_mapping(self):
        company_tech_stack_relations = []  
        existing_tech_stacks = set()  
        mapping_id = 1

        print("회사 테크 스택 매핑 진행중")

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    technical_tags = self.fetch_company_technical_tags(company_id)
                    for tech_stack in technical_tags:
                        tech_stack_id = tech_stack['id']
                        if tech_stack_id not in existing_tech_stacks:
                            existing_tech_stacks.add(tech_stack_id)
                            company_tech_stack_relations.append({
                                "id" : mapping_id,
                                "company_id": company_id,
                                "tech_stack_id": tech_stack_id
                            })
                            mapping_id += 1
                print((f"{page} 페이지 진행 완료."))


        with open(self.company_tech_stack_file_path, 'w', encoding='utf-8') as company_tech_stack_file:
            json.dump(company_tech_stack_relations, company_tech_stack_file, ensure_ascii=False, indent=4)
        
        print(f"회사와 기술 스택 관계 데이터를 {self.company_tech_stack_file_path}에 저장했습니다.")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 10
    data_folder = 'api_data'

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder)
    fetcher.generate_unique_tech_stacks_and_mapping()
