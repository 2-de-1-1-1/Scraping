import requests
import json
import os

#job_position_mapping 테이블에 데이터를 전처리하는 스크립트입니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.filtered_data = []  # 필요한 데이터만 담을 리스트를 초기화
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def fetch_data(self):
        unique_id = 1  # 각 position에 고유한 ID를 할당하기 위한 카운터
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'jobPositions' in data:
                    for job in data['jobPositions']:
                        for category_id in job["jobCategoryIds"]:
                            # 분할된 데이터를 필터링된 리스트에 추가
                            self.filtered_data.append({
                                "id": unique_id,
                                "job_id": job["id"],
                                "position_id": category_id
                            })
                            unique_id += 1  # 고유 ID 증가
                    print(f"Fetched data from page {page}")
                else:
                    print(f"The 'jobPositions' key is missing in the response from page {page}.")
                    break
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break
        
        # 결과 데이터 파일로 저장
        file_name = "job_position_mapping_api.json"
        file_path = os.path.join(self.folder, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.filtered_data, file, ensure_ascii=False, indent=4)
        print(f"Saved split data to {file_name}")

if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
