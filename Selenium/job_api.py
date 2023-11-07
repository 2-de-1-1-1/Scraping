import requests
import json
import os

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='job_api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                file_name = f"page_{page}.json"
                file_path = os.path.join(self.folder, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                
                print(f"Saved {file_name}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break  

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 70
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
