import requests
import json
import os

#job api에서 tech stack을 임시저장한 다음 tech stack의 유니크 값을 만들어 이와 비교해 job과 tech_stack을 매핑하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.unique_technical_tags = {} 
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_and_extract_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                jobs_data = response.json().get('jobPositions', [])
                for job in jobs_data:
                    for tag in job.get("technicalTags", []):
                        self.unique_technical_tags[tag["id"]] = {"id": tag["id"], "name": tag["name"]}
                print(f"Fetched and extracted data from page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

    def create_and_save_tech_mapping(self):
        mapping_data = []
        unique_id = 1 

        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                jobs_data = response.json().get('jobPositions', [])
                for job in jobs_data:
                    job_id = job["id"]
                    for tag in job.get("technicalTags", []):
                        mapping_data.append({
                            "id": unique_id,
                            "job_id": job_id,
                            "tech_id": tag["id"]
                        })
                        unique_id += 1
                print(f"Created tech mappings for page {page}")
            else:
                print(f"Failed to fetch data for tech mapping from page {page}. Status code: {response.status_code}")
                break

        self.save_data_to_file("job_tech_mapping_api.json", mapping_data)

    def save_data_to_file(self, filename, data):
        file_path = os.path.join(self.folder, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Saved extracted data to {filename}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71 

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data() 
    fetcher.create_and_save_tech_mapping() 
