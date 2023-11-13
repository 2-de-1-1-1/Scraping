import requests
import MySQLdb
import datetime
import sys
from fetcher import ApiFetcher
from logging_config import *

logger = logging.getLogger(script_name)


class LocationInfoFetcher(ApiFetcher):
    def __init__(self, start_page, end_page):
        super().__init__(start_page, end_page)

    def fetch_job_positions(self, page):
        logger.info(f"페이지 {page} 의 정보를 가져오는 중...")
        response = requests.get(f"{self.base_job_url}{page}")
        return response.json() if response.status_code == 200 else None

    def fetch_company_geo(self, company_id):
        if company_id in self.companies_seen:
            return None
        response = requests.get(f"{self.base_company_url}{company_id}")
        if response.status_code == 200:
            self.companies_seen.add(company_id)
            company_data = response.json()['company']
            return {
                'id': company_data.get('id'),
                'address': company_data.get('address', ''),
                'latitude': company_data.get('latitude', None),
                'longitude': company_data.get('longitude', None)
            }
        else:
            return None

    def insert_data_to_db(self, company_data):

        insert_query = '''
            INSERT INTO location_info (id, address, geo_lat, geo_alt, created_at, modified_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=%s, address=%s, geo_lat=%s, geo_alt=%s, modified_at=%s
        '''
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = tuple(company_data.values()) + (now, now,) + tuple(company_data.values()) + (now,)
        self.cursor.execute(insert_query, params)
        self.conn.commit()

    def check_location_exists(self, location_id):
        query = "SELECT id FROM location_info WHERE id = %s"
        self.cursor.execute(query, (location_id,))
        return self.cursor.fetchone() is not None

    def fetch_data(self):
        for page in range(self.start_page, self.end_page + 1):
            logger.info(f"페이지 {page} 작업 중")
            job_data = self.fetch_job_positions(page)
            if job_data:
                for job in job_data['jobPositions']:
                    company_id = job['companyId']
                    company_info = self.fetch_company_geo(company_id)
                    if company_info and company_info['address']:
                        self.insert_data_to_db(company_info)
            logger.info(f"페이지 {page} 작업 완료")
        logger.info("모든 페이지 작업 완료")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python location_info.py start_page end_page")
        sys.exit(1)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])
    fetcher = LocationInfoFetcher(start_page=start_page, end_page=end_page)
    fetcher.fetch_data()
