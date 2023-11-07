import requests
import json
import os

# 저장할 폴더 이름
folder_name = 'job_api_data'

# 해당 폴더가 없으면 생성
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 페이지 인덱스 시작 번호
start_page_index = 1  # 시작 페이지 번호 설정
max_empty_pages = 5  # 최대 연속 비어 있는 페이지 수

empty_pages_count = 0

# 페이지를 순회하면서 데이터를 가져오고 파일로 저장
while True:
    # URL 구성
    url = f"https://career.programmers.co.kr/api/job_positions?page={start_page_index}"
    response = requests.get(url)
    
    # 응답이 성공적인지 확인
    if response.status_code == 200:
        data = response.json()

        # 데이터가 비어 있는지 확인
        if data['jobPositions']:  # 또는 len(data['jobPositions']) > 0으로 확인할 수도 있습니다.
            # 파일 이름 설정 (예: page_1.json)
            file_name = f"page_{start_page_index}.json"
            file_path = os.path.join(folder_name, file_name)
            
            # 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print(f"Saved {file_name}")
            start_page_index += 1  # 다음 페이지 인덱스로 이동
            empty_pages_count = 0  # 비어 있는 페이지 수 리셋
        else:
            # 데이터가 비어 있다면 카운트 증가
            empty_pages_count += 1
            if empty_pages_count >= max_empty_pages:
                # 연속된 비어 있는 페이지가 max_empty_pages에 도달하면 중단
                print("Reached the end of the pages with data.")
                break
            else:
                # 다음 페이지를 확인하기 위해 인덱스 증가
                start_page_index += 1
    else:
        print(f"Failed to fetch data from page {start_page_index}. Status code: {response.status_code}")
        break  # 요청에 실패한 경우 중단
