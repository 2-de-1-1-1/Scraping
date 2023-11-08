import requests
import json
import os

#welfare 테이블 데이터를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder
        self.output_file = 'welfare_api.json'
        self.output_file_path = os.path.join(self.data_folder, self.output_file)
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
        self.benefits = set()

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch job positions from page {page}. Status code: {response.status_code}")
            return None

    def fetch_company_benefits(self, company_id):
        if company_id in self.companies_seen:
            return None
        self.companies_seen.add(company_id)
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            company_data = response.json()
            return company_data['company'].get('benefitTags', [])
        else:
            print(f"Failed to fetch company benefits for company ID {company_id}. Status code: {response.status_code}")
            return []

    def fetch_and_save_unique_benefits(self):
        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    benefits = self.fetch_company_benefits(company_id)
                    if benefits:
                        self.benefits.update(benefits)

        # Assign a unique ID to each benefit and save to list
        unique_benefits_data = [{"id": idx + 1, "name": benefit} for idx, benefit in enumerate(self.benefits)]

        # Save the unique benefits to a file
        with open(self.output_file_path, 'w', encoding='utf-8') as file:
            json.dump(unique_benefits_data, file, ensure_ascii=False, indent=4)

        print(f"Saved unique benefits data to {self.output_file_path}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71 
    data_folder = 'api_data'

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder)
    fetcher.fetch_and_save_unique_benefits()
