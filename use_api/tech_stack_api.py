import requests
import json
import os

#tech_stack 테이블의 데이터를 전처리 하는 스크립트 입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.extracted_data = []  # 추출된 데이터를 저장할 리스트를 초기화
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_and_extract_data(self):
        unique_technical_tags = {}  # 중복을 방지하기 위해 딕셔너리 사용

        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                jobs_data = response.json().get('jobPositions', [])
                for job in jobs_data:
                    for tag in job.get("technicalTags", []):
                        # 딕셔너리에 유니크하게 기술 태그 저장
                        unique_technical_tags[tag["id"]] = {"id": tag["id"], "name": tag["name"]}
                print(f"Fetched and extracted data from page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

        # 중복 제거된 기술 태그만 리스트에 추가
        self.extracted_data = list(unique_technical_tags.values())

        # 추출된 데이터를 파일에 저장
        self.save_data_to_file()




    def save_data_to_file(self):
        file_name = "tech_stack_api.json"
        file_path = os.path.join(self.folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.extracted_data, file, ensure_ascii=False, indent=4)
        print(f"Saved extracted data to {file_name}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data()
