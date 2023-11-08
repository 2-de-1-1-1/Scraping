import requests
import json
import os

# API 데이터를 가져오는 클래스 정의
class JobApiFetcher:
    def __init__(self, start_page, end_page, data_folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.data_folder = data_folder  # 데이터를 저장할 폴더
        self.output_file = os.path.join(self.data_folder, 'company_data.json')  # 파일 경로를 폴더와 함께 설정
        self.all_data = []  # 모든 데이터를 저장할 리스트

        # 데이터 폴더가 없으면 생성합니다.
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                self.all_data.extend(data['jobPositions'])  # 전체 데이터에 추가
                
                print(f"Processed page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break

        self.save_data()

    def save_data(self):
        # 모든 페이지 처리 후 데이터 저장
        with open(self.output_file, 'w', encoding='utf-8') as file:
            json.dump(self.all_data, file, ensure_ascii=False, indent=4)
            print(f"Data saved to {self.output_file}")

# 메인 실행 구문
if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71
    
    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_data()
