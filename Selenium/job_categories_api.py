import requests
import json

def save_api_data_as_json(url, file_name):
    # API에서 데이터 가져오기
    response = requests.get(url)
    
    # 요청이 성공했는지 확인
    if response.status_code == 200:
        data = response.json()
        
        # JSON 파일로 저장
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Data has been saved to {file_name}")
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")

# 사용 예
save_api_data_as_json('https://career.programmers.co.kr/api/job_positions/job_categories', 'job_categories.json')
