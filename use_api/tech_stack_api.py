import requests
import json
import os

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page  # 시작 페이지
        self.end_page = end_page  # 종료 페이지
        self.data_folder = data_folder  # 데이터를 저장할 폴더
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


    def generate_unique_tech_stacks(self):
        unique_tech_stacks = []
        existing_tech_stack_ids = set()

        print(f"총 {self.end_page - self.start_page + 1}개의 페이지를 처리합니다...")

        for page in range(self.start_page, self.end_page + 1):
            print(f"{page} 페이지를 처리 중...")
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    technical_tags = self.fetch_company_technical_tags(company_id)
                    for tech_stack in technical_tags:
                        tech_stack_id = tech_stack['id']
                        if tech_stack_id not in existing_tech_stack_ids:
                            existing_tech_stack_ids.add(tech_stack_id)
                            unique_tech_stacks.append({
                                "id": tech_stack['id'],
                                "name": tech_stack['name']
                            })

        print("고유 기술 스택 추출을 완료하였습니다.")
        self.save_tech_stacks_to_file(unique_tech_stacks)  # 저장 메서드 호출


    def save_tech_stacks_to_file(self, tech_stacks):
        unique_tech_stacks_file_path = os.path.join(self.data_folder, 'tech_stack_api.json')
        with open(unique_tech_stacks_file_path, 'w', encoding='utf-8') as file:
            json.dump(tech_stacks, file, ensure_ascii=False, indent=4)
        print(f"고유 기술 스택 데이터가 {unique_tech_stacks_file_path}에 저장되었습니다.")

# 스크립트 실행 부분
if __name__ == "__main__":
    start_page_index = 1  
    end_page_index = 71
    data_folder = 'api_data'  

    # JobApiFetcher 인스턴스 생성 및 메소드 호출
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder)
    fetcher.generate_unique_tech_stacks()
