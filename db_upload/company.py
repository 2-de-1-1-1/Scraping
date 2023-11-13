import datetime
import sys
import requests
from fetcher import ApiFetcher
from logging_config import *

logger = logging.getLogger(script_name)


class CompanyApiFetcher(ApiFetcher):
    def __init__(self, start_page, end_page):
        super().__init__(start_page, end_page)

    def fetch_job_positions(self, page):
        response = requests.get(self.base_job_url + str(page))
        if response.status_code == 200:
            logger.info(f"페이지 {page}: 직무 정보를 성공적으로 가져왔습니다.")
            return response.json()
        else:
            logger.info(f"페이지 {page}: 직무 정보 가져오기 실패. 상태 코드: {response.status_code}")
            return None

    def check_company_exists(self, company_id):
        self.cursor.execute("SELECT COUNT(1) FROM Company WHERE id=?", company_id)
        return self.cursor.fetchone()[0] > 0

    def upload_company_data(self, company_data):
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시간
            insert_query = '''
            INSERT INTO Company (id, name, num_employees, investment, revenue, homepage, loc_info_id, created_at, modified_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, num_employees=%s, investment=%s, revenue=%s, homepage=%s, loc_info_id=%s, modified_at=%s
            '''
            values = (
                company_data['id'],
                company_data['name'],
                company_data.get('num_employees'),
                company_data.get('investment'),
                company_data.get('revenue'),
                company_data.get('homepage'),
                company_data.get('loc_info_id'),
                now,
                now,
                company_data['name'],
                company_data.get('num_employees'),
                company_data.get('investment'),
                company_data.get('revenue'),
                company_data.get('homepage'),
                company_data.get('loc_info_id'),
                now,
            )
            self.cursor.execute(insert_query, values)
            self.conn.commit()
        except Exception as e:
            logger.info(f"기업 ID {company_data['id']} 추가 중 오류가 발생했습니다: {e}")


def preprocess_company(company_data):
    investment = company_data.get('funding')
    revenue = company_data.get('revenue')
    address = company_data.get('address')

    new_company_data = {
        'id': company_data['id'],
        'name': company_data['name'],
        'num_employees': company_data.get('employeesCount'),
        'investment': None if investment is None or investment == 0 else int(investment * 1000000),
        'revenue': None if revenue is None or revenue == 0 else int(revenue * 1000000),
        'homepage': company_data.get('homeUrl'),
        'loc_info_id': None if not address else company_data['id'],
    }

    return new_company_data


def fetch_and_upload_companies(fetcher, start_page, end_page):
    processed_companies = set()
    for page in range(start_page, end_page + 1):
        url = f"https://career.programmers.co.kr/api/job_positions?page={page}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for job_data in data['jobPositions'][:22]:
                company_info = job_data.get('company')
                if company_info:
                    company_id = company_info['id']
                    if company_id not in processed_companies:
                        processed_companies.add(company_id)
                        processed_company_data = preprocess_company(company_info)
                        fetcher.upload_company_data(processed_company_data)  # 업로드
            logger.info(f"페이지 {page} 처리 완료.")
        else:
            logger.info(f"페이지 {page} 처리 실패, 상태 코드: {response.status_code}")
            break

    logger.info("모든 기업 데이터가 서버 데이터베이스에 업로드되었습니다.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    fetcher = CompanyApiFetcher(start_page=start_page, end_page=end_page)
    fetch_and_upload_companies(fetcher, start_page, end_page)
