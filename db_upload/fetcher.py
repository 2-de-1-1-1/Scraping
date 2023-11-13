import MySQLdb
import os


class ApiFetcher:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.base_job_url = "https://career.programmers.co.kr/api/job_positions?page="
        self.base_company_url = "https://career.programmers.co.kr/api/companies/"
        self.companies_seen = set()
        self.conn = MySQLdb.connect(
            host=os.environ.get('AZURE_MYSQL_HOST'),
            database=os.environ.get('AZURE_MYSQL_NAME'),
            user=os.environ.get('AZURE_MYSQL_USER'),
            password=os.environ.get('AZURE_MYSQL_PASSWORD')
        )
        self.cursor = self.conn.cursor()