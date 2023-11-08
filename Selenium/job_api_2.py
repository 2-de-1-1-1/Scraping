import requests
import json
import os

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.all_data = []  # 모든 페이지 데이터를 담을 리스트를 초기화
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'jobPositions' in data:
                    self.all_data.extend(data['jobPositions'])  # 페이지 데이터를 리스트에 추가
                    print(f"Fetched data from page {page}")
                else:
                    print(f"The 'jobPositions' key is missing in the response from page {page}.")
                    break
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break
        
        file_name = "job_data.json"
        file_path = os.path.join(self.folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.all_data, file, ensure_ascii=False, indent=4)
        print(f"Saved all data to {file_name}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 3
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
