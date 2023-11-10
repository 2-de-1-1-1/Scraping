import requests
import json
import os
from config import *
import pyodbc

#position 테이블의 데이터를 전처리하는 스크립트입니다.

server = 'de-2-111-db.database.windows.net'
database = 'de-2-111'
username = 'dbadmin'
password = 'pa$$w0rd'
driver = '{ODBC Driver 18 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def insert_data_to_table(cursor, extracted_data):
    try:
        for page_data in extracted_data:  
            for record in page_data: 
                insert_query = '''INSERT INTO position (id, name, created_at, modified_at)
                                VALUES (?, ?, GETDATE(), GETDATE())'''
                values = (record['id'], record['name'])  # 딕셔너리의 키를 사용하여 값 추출
                cursor.execute(insert_query, values)
        cursor.commit()  # 모든 레코드 삽입 시도 후 한 번만 커밋합니다.
    except Exception as e:  # 모든 예외를 캐치합니다.
        print(f"An error occurred: {e}")
        cursor.rollback()  # 에러가 발생하면 롤백합니다.

class JobApiFetcher:
    def __init__(self, start_page, end_page, folder='api_data'):
        self.start_page = start_page
        self.end_page = end_page
        self.folder = folder
        self.base_url = "https://career.programmers.co.kr/api/job_positions/job_categories"
        self.extracted_data = [] 
        self.conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        self.cursor = self.conn.cursor()


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
    
    def insert_data_to_table(cursor, extracted_data):
        try:
            for page_data in extracted_data:  
                for record in page_data: 
                    insert_query = '''INSERT INTO position (id, name, created_at, modified_at)
                                    VALUES (?, ?, GETDATE(), GETDATE())'''
                    values = (record['id'], record['name']) 
                    cursor.execute(insert_query, values)
            cursor.commit() 
        except Exception as e: 
            print(f"An error occurred: {e}")
            cursor.rollback()  

    def save_data_to_db(self):
        insert_data_to_table(cursor, self.extracted_data)
        print("db에 저장")


if __name__ == "__main__":
    start_page_index = 1 
    end_page_index = 1    

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)
    fetcher.fetch_and_extract_data()
    fetcher.save_data_to_db()

    cursor.close()
    conn.close()
