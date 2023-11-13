import datetime
import sys

import requests

from fetcher import ApiFetcher
from logging_config import *

logger = logging.getLogger(script_name)


class CompanyWelfareFetcher(ApiFetcher):
    def __init__(self, start_page, end_page):
        super().__init__(start_page, end_page)
        self.inserted_company_welfare_pairs = set()

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            return response.json()
        else:
            logger.info(f"페이지 {page}에서 직무 정보를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return None

    def fetch_company_welfare(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(self.base_company_url + str(company_id))
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            data = response.json()
            return data['company'].get('benefitTags', [])
        else:
            logger.info(f"회사 ID {company_id}에 대한 welfare를 가져오는데 실패했습니다. 상태 코드: {response.status_code}")
            return []

    def fetch_data(self):
        all_benefit_data = []

        for page in range(self.start_page, self.end_page + 1):
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    benefits = self.fetch_company_welfare(company_id)
                    if benefits is not None:
                        for benefit in benefits:
                            all_benefit_data.append({
                                'company_id': company_id,
                                'welfare_name': benefit
                            })

            logger.info(f"{page}페이지 진행중")

        return all_benefit_data

    def welfare_name_exists(self, welfare_name):
        check_query = "SELECT COUNT(*) FROM welfare WHERE name = %s"
        self.cursor.execute(check_query, (welfare_name,))
        return self.cursor.fetchone()[0] > 0

    def upload_welfare_data(self, all_benefit_data):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO welfare (name, created_at, modified_at)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE modified_at=%s
        '''

        for data in all_benefit_data:
            company_id = data["company_id"]
            welfare_name = data["welfare_name"]
            if not self.welfare_name_exists(welfare_name):
                values = (
                    data["welfare_name"],
                    now,
                    now,
                    now
                )
                try:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"{data['welfare_name']} welfare에 업로드")
                except Exception as e:
                    logger.info(f"welfare 데이터 삽입 중 오류 발생 : name {data['welfare_name']} - {e}")
                    self.conn.rollback()

    def get_welfare_id(self, welfare_name):
        query = "SELECT id FROM welfare WHERE name = %s"
        self.cursor.execute(query, (welfare_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def upload_company_welfare_mapping_data(self, all_benefit_data):
        self.cursor.execute('truncate company_welfare_mapping')
        self.conn.commit()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = '''
        INSERT INTO company_welfare_mapping (company_id, welfare_id, created_at, modified_at)
        VALUES (%s, %s, %s, %s)
        '''

        for data in all_benefit_data:
            company_id = data["company_id"]
            welfare_name = data["welfare_name"]
            welfare_id = self.get_welfare_id(welfare_name)

            if not self.check_company_welfare_pair_exists(company_id, welfare_id):
                values = (
                    data["company_id"],
                    welfare_id,
                    now,
                    now
                )
                try:
                    self.cursor.execute(insert_query, values)
                    self.conn.commit()
                    logger.info(f"{data['welfare_name']} company_welfare_mapping 업로드")
                    self.inserted_company_welfare_pairs.add((company_id, welfare_id))
                except Exception as e:
                    logger.info(f"company_welfare_mapping 삽입 중 오류 발생 : name {data['welfare_name']} - {e}")
                    self.conn.rollback()
            else:
                logger.info(f"{data['welfare_name']} company_welfare_mapping 중복 데이터로 처리됨")

    def check_company_welfare_pair_exists(self, company_id, welfare_id):
        select_query = '''
        SELECT id FROM company_welfare_mapping WHERE company_id = %s AND welfare_id = %s
        '''
        self.cursor.execute(select_query, (company_id, welfare_id))
        row = self.cursor.fetchone()
        return row is not None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    fetcher = CompanyWelfareFetcher(start_page=start_page, end_page=end_page)
    all_benefit_data = fetcher.fetch_data()
    fetcher.upload_welfare_data(all_benefit_data)
    fetcher.upload_company_welfare_mapping_data(all_benefit_data)
