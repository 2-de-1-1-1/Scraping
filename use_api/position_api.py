import requests
import json
import os

#position 테이블의 데이터를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.base_url = "https://career.programmers.co.kr/api/job_positions/job_categories"
        self.extracted_data = [] 
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_and_extract_data(self):
        for page in range(self.start_page, self.end_page + 1):
            params = {'page': page}
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                page_data = response.json()
                self.extracted_data.append(page_data)
                print(f"Fetched and extracted data from page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

    def save_data_to_file(self):
        file_name = "position_api.json"
        file_path = os.path.join(self.folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.extracted_data, file, ensure_ascii=False, indent=4)
        print(f"Saved extracted data to {file_path}")

if __name__ == "__main__":
    start_page_index = 1 
    end_page_index = 1    

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data()
    fetcher.save_data_to_file()
