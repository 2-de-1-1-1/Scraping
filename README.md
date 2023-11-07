## 프로그래머스 커리어 페이지 스크래핑입니다

chrome 브라우저로 스크래핑합니다.
config.py에서 개인 user_agent, chrom_driver_path를 설정해주세요.
터미널이나 cmd에서 해당 파일을 실행하면 됩니다. (ex. py job.py)

- scrape_page : 각 세부페이지로 이동하고 해당 페이지에서 필요한 정보를 스크래핑합니다. idx로 스크래핑할 페이지 인덱스를 설정할 수 있습니다.
- scrape_title : 공고명을 스크랩합니다.
- scarpe_company_name : 회사명을 스크랩합니다.
- scarpe_informaion : 직무, 지원 마감, 고용형태 등의 정보를 스크랩합니다.
- scrape_requied_techstack : 기업이 요구하는 기술스택을 스크랩합니다.

### 사용법
```python
if __name__ == "__main__":
    collected_data = []
    try:
        for page_number in range(1,5):
            scrape = Scrape(f"https://career.programmers.co.kr/job?page={page_number}&order=recent")
            
            for idx in range(1,22):
                try :
                    data = scrape.scrape_page(idx)
                    if data:
                        collected_data.append(data)
                except Exception as e:
                    print(f"페이지 {page_number}, 항목{idx}에서 에러 발생: {e}")

    except KeyboardInterrupt:
        print("\n 스크래핑을 강제 중단합니다. json으로 백업합니다.")
        with open('collected_data.json', 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=4)
```
page_number는 페이지 범위 입니다.

idx는 해당 페이지에서 스크래핑할 세부 인덱스입니다.

timeoutexception 등 오류가 생기면 해당 페이지, idx에서 오류가 발생했다고 표기하고 스크래핑을 진행합니다.

오류가 너무 많이 발생하거나 다른 이유로 강제종료시 그 동안 스크래핑한 데이터를 백업합니다.

