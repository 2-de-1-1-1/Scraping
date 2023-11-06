## 프로그래머스 커리어 페이지 스크래핑입니다

chrome 브라우저로 스크래핑합니다.
user_agent 부분은 개인 agent로 수정해주세요.
- scrape_page : 각 세부페이지로 이동하고 해당 페이지에서 필요한 정보를 스크래핑합니다. idx로 스크래핑할 페이지 인덱스를 설정할 수 있습니다.
- scrape_title : 공고명을 스크랩합니다.
- scarpe_company_name : 회사명을 스크랩합니다.
- scarpe_informaion : 직무, 지원 마감, 고용형태 등의 정보를 스크랩합니다.
- scrape_requied_techstack : 기업이 요구하는 기술스택을 스크랩합니다.

### 사용법
```python
for idx in range(1,n):
    scrape.scrape_page(idx)
    
    print(scrape.all_data)
```
에서 원하는 인덱스를 입력하고 터미널에서 실행하면 됩니다.
현재 프로그래머스 커리어 사이트는 한페이지당 26개의 공고를 보여주고, 마지막 4개는 원티드로 연결되는 페이지입니다.
