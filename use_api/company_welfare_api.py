import requests
import json
import os

class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data', output_file='benefit_data.json'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder  #
        self.output_file = os.path.join(self.data_folder, output_file)  
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()


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
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id) 
            data = response.json()
            return data['company'].get('benefitTags', [])
        else:
            print(f"Failed to fetch company benefits for company ID {company_id}. Status code: {response.status_code}")
            return []

    def fetch_data(self):
        all_benefit_data = []

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    benefits = self.fetch_company_benefits(company_id)
                    if benefits is not None:  
                        all_benefit_data.append({
                            'company_id': company_id,
                            'welfare': benefits
                        })


        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(all_benefit_data, file, ensure_ascii=False, indent=4)
        
        print(f"Saved all data to {self.output_file}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    data_folder = 'api_data'  
    output_file = 'company_welfare_api.json'  


    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index, data_folder=data_folder, output_file=output_file)
    fetcher.fetch_data()
