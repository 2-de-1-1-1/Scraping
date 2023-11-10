## api 데이터 전처리 및 db 업로드

프로그래머스 공고 페이지와 기업 페이지에서 api를 가져와 전처리하고 db에 업로드합니다.

실행방법

db_upload.py에 

원하는 범위를 지정하고

해당 파일을 실행시키면 됩니다.


```python
start_page = 1
end_page = 3


scripts = [
    "location_info.py",
    "company.py",
    "job.py",
    "company_welfare_mapping.py",
    "tech_stack.py",
    "company_tech_mapping.py",
    "job_tech_mapping.py",
    "job_position_mapping.py"
]
```

