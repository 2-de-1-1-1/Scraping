import requests
import json
import os

# job 원본 api에서 주소 데이터만을 추출하는 스크립트입니다.

class JobApiAddressFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.address_data = [] 
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'jobPositions' in data:
                    for job in data['jobPositions']:
                        self.address_data.append({
                            'id': job['id'],
                            'address': job['address'],
                            'geo_lat': None, 
                            'geo_lng': None  
                        })
                    print(f"Fetched data from page {page}")
                else:
                    print(f"The 'jobPositions' key is missing in the response from page {page}.")
                    break
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break
        
        self.save_data_to_json()

    def save_data_to_json(self):
        file_name = "location_info_api.json"
        file_path = os.path.join(self.folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.address_data, file, ensure_ascii=False, indent=4)
        
        print(f"Saved all address data to {file_name}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiAddressFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
