import requests
import datetime
import json
from config import *
import pyodbc

class JobApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page  # 시작 페이지
        self.end_page = end_page  # 종료 페이지
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.tech_stack = set()
        self.companies_seen = set()
        self.conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.cursor = self.conn.cursor()


    def fetch_job_tech_stack(self, page):
        response = requests.get(f"{self.base_job_url}{page}")
        if response.status_code == 200:
            job_data = response.json().get('jobPositions', [])  # JSON 문자열 파싱
            for job in job_data:
                technical_tags = job.get('technicalTags', [])
                for tag in technical_tags:
                    tag_id = tag.get('id')
                    tag_name = tag.get('name')
                    if tag_id and tag_name:
                        self.tech_stack.add((tag_id, tag_name))
            return True
        else:
            print(f"{page} 페이지 실패했습니다. 상태 코드: {response.status_code}")
            return False


    def fetch_company_tech_stack(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            data = response.json()
            technical_tags = [
                {'id': tag['id'], 'name': tag['name']}
                for tag in data['company'].get('technicalTags', [])
            ]
            
            # 기존 기술 태그 집합에 추가
            for tag in technical_tags:
                self.tech_stack.add((tag['id'], tag['name']))
            
            return technical_tags
        else:
            print(f"실패 {company_id}. Status code: {response.status_code}")
            return []

    def upload_tech_stack_to_db(self):
        # 수집된 데이터를 set에서 dict로 변환
        tech_stack_dict = {tech_id: tech_name for tech_id, tech_name in self.tech_stack}

        try:
            conn = pyodbc.connect(
                f'DRIVER={driver};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
            )
            cursor = conn.cursor()

            # 기술 스택 데이터를 tech_stack 테이블에 추가
            for tech_id, tech_name in tech_stack_dict.items():
                cursor.execute("""
                    INSERT INTO tech_stack (id, name, created_at, modified_at)
                    VALUES (?, ?, ?, ?)
                """, (tech_id, tech_name, datetime.datetime.now(), datetime.datetime.now()))
            
            conn.commit()
            print("기술 스택 데이터를 데이터베이스에 업로드했습니다.")
        except Exception as e:
            print(f"데이터베이스 업로드 중 오류 발생: {str(e)}")
        finally:
            cursor.close()
            conn.close()




# 스크립트 실행 부분
if __name__ == "__main__":
    start_page = 1  
    end_page = 71

    # JobApiFetcher 인스턴스 생성
    fetcher = JobApiFetcher(start_page, end_page)

    # 여러 페이지의 기술 스택 수집
    for page_index in range(start_page, end_page + 1):
        success = fetcher.fetch_job_tech_stack(page_index)
        if not success:
            print(f"{page_index} 페이지의 기술 스택 수집 실패")

    # 데이터베이스에 기술 스택 업로드
    fetcher.upload_tech_stack_to_db()