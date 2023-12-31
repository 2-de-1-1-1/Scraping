import datetime

import requests

from fetcher import ApiFetcher


class PositionApiFetcher(ApiFetcher):
    def __init__(self, start_page, end_page):
        super().__init__(start_page, end_page)
        self.base_url = "https://career.programmers.co.kr/api/job_positions/job_categories"
        self.extracted_data = []  # 추출된 데이터를 저장할 리스트를 초기화

    def fetch_and_insert(self):
        response = requests.get(self.base_url)
        if response.status_code == 200:
            page_data = response.json()
            self.extracted_data.append(page_data)
        else:
            return

        for position in response.json():
            self.do_insert(position)

    def do_insert(self, position):
        insert_sql = '''
        INSERT INTO position (id, name, created_at, modified_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE id=%s, name=%s, modified_at=%s
        '''
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = tuple(position.values()) + (now, now) + tuple(position.values()) + (now,)
        self.cursor.execute(insert_sql, values)
        self.conn.commit()


    def fetch_and_extract_data(self):
        for page in range(self.start_page, self.end_page + 1):
            params = {'page': page}
            response = requests.get(self.base_url, params=params)

            if response.status_code == 200:
                page_data = response.json()
                self.extracted_data.append(page_data)
                print(f"Fetched and extracted data from page {page}")
            else:
                print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
                break


if __name__ == "__main__":
    start_page = 1
    end_page = 1

    fetcher = PositionApiFetcher(start_page=start_page, end_page=end_page)
    fetcher.fetch_and_insert()
