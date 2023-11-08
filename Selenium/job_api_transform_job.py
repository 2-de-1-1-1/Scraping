import json
from datetime import datetime

# 주어진 JSON 객체를 파싱하여 새로운 JSON 형식으로 변환하는 함수
def preprocess_json(job_data):
    # 'careerRange'에 따른 경력 값 설정
    if job_data.get('careerRange') == '신입 채용':
        min_experience = 0
        max_experience = 0
    elif job_data.get('careerRange') == '경력 무관':
        min_experience = 0
        max_experience = 99
    elif job_data.get('careerRange'):
        career_range = job_data['careerRange'].split('...')
        min_experience = int(career_range[0])
        # '...' 다음에 값이 없다면 최대 경력을 99로 설정
        max_experience = int(career_range[1]) if len(career_range) > 1 else 99
    else:
        min_experience = 0
        max_experience = 99  # 기본값 설정

    # 데이터 변환 작업
    new_job_data = {
        'id': job_data['id'],
        'name': job_data['title'],
        'company_id': job_data['companyId'],
        'work_type': job_data['jobType'],
        'due_datetime': '2999-12-31T23:59:59+09:00' if job_data['period'] == '상시 채용' else job_data['startAt'],
        'min_wage': job_data['minSalary'],
        'max_wage': job_data['maxSalary'],
        'min_experience': min_experience,
        'max_experience': max_experience,
        'loc_info_id': None,
        'created_at': job_data['createdAt'],
        'modified_at': job_data['updatedAt']
    }
    
    # ensure_ascii=False를 추가하여 한글이 유니코드로 이스케이프되지 않도록 함
    return json.dumps(new_job_data, indent=4, ensure_ascii=False)

# JSON 파일 읽기
with open('page_1.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    job_positions = data['jobPositions']  # "jobPositions" 키로 데이터 접근

# 각각의 job 데이터를 새로운 형식으로 전처리
preprocessed_json_list = [preprocess_json(job) for job in job_positions]

# 결과 출력 및 파일로 저장
with open('preprocessed_job_data_page_1.json', 'w', encoding='utf-8') as new_file:
    # 리스트를 JSON 배열로 저장하기 위해 "["와 "]"를 추가합니다.
    new_file.write("[\n")
    for job_json in preprocessed_json_list[:-1]:  # 마지막 콤마를 추가하지 않기 위해
        new_file.write(f"{job_json},\n")
    new_file.write(f"{preprocessed_json_list[-1]}\n")  # 마지막 아이템 처리
    new_file.write("]")
