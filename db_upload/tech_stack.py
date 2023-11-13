import datetime
import sys

import requests

from fetcher import ApiFetcher
from logging_config import *

logger = logging.getLogger(script_name)


class TechStackFetcher(ApiFetcher):
    def __init__(self, start_page, end_page):
        super().__init__(start_page, end_page)
        self.tech_stack = set()

    def fetch(self):
        for page in range(start_page, end_page):
            self.fetch_job_tech_stack(page)

    def fetch_job_tech_stack(self, page):
        response = requests.get(f"{self.base_job_url}{page}")
        if response.status_code == 200:
            job_data = response.json().get('jobPositions', [])
            for job in job_data:
                technical_tags = job.get('technicalTags', [])
                for tag in technical_tags:
                    tag_id = tag.get('id')
                    tag_name = tag.get('name')
                    if tag_id and tag_name:
                        self.tech_stack.add((tag_id, tag_name))
            logger.info(f"페이지 {page}의 테크 스택 데이터 수집 완료")
            return True
        else:
            logger.info(f"{page} 페이지 실패했습니다. 상태 코드: {response.status_code}")
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
            for tag in technical_tags:
                self.tech_stack.add((tag['id'], tag['name']))
            logger.info(f"회사 ID {company_id}의 테크 스택 데이터 수집 완료")
            return technical_tags
        else:
            logger.info(f"실패 {company_id}. Status code: {response.status_code}")
            return []

    def upload_tech_stack_to_db(self):
        tech_stack_dict = {tech_id: tech_name for tech_id, tech_name in self.tech_stack}

        try:
            for tech_id, tech_name in tech_stack_dict.items():
                self.cursor.execute("""
                    INSERT INTO tech_stack (id, name, created_at, modified_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE name=%s, modified_at=%s
                """, (tech_id, tech_name, datetime.datetime.now(), datetime.datetime.now(), tech_name, datetime.datetime.now()))
            self.conn.commit()
            logger.info("테크 스택 데이터를 데이터베이스에 업로드했습니다.")
        except Exception as e:
            logger.info(f"데이터베이스 업로드 중 오류 발생: {str(e)}")
        finally:
            self.cursor.close()
            self.conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    fetcher = TechStackFetcher(start_page, end_page)
    fetcher.fetch()
    fetcher.upload_tech_stack_to_db()
