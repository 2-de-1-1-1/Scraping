## api 데이터 전처리 및 db 업로드

프로그래머스 공고 페이지와 기업 페이지에서 api를 가져와 전처리하고 db에 업로드합니다.

실행방법

```python
if __name__ == "__main__":
    start_page_index = 1
    end_page_index = 71

    fetcher = JobApiFetcher(start_page=start_page_index, end_page=end_page_index)

    fetcher.process_job_data_pages()
```
원하는 페이지 인덱스를 입력하고 터미널에서 실행시키면됩니다.

실행 순서

location_info

company

job

company_welfare_mapping

tech_stack

company_tech_mapping

job_tech_mapping

job_position_mapping

