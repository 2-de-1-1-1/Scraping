## 프로그래머스 커리어 페이지 스크래핑입니다

chrome 브라우저로 스크래핑합니다.
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
    error_messages = []
    completed_successfully = False

    save_dir = 'job_data'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    try:
        for page_number in range(1, 3):
            scrape = Scrape(f"https://career.programmers.co.kr/job?page={page_number}&order=recent")
            for idx in range(1, 4):
                try:
                    data = scrape.scrape_page(idx)
                    job_id = data.get('id', None)
                    if data:
                        collected_data.append(data)
                except Exception as e:
                    error_msg = f"페이지 {page_number}, 항목 {idx} 에서 에러 발생: {str(e)}"
                    print(error_msg)
                    error_messages.append(error_msg)

        completed_successfully = True

    except KeyboardInterrupt:
        print("\n스크래핑을 사용자에 의해 강제 중단합니다.")
        error_messages.append("스크래핑이 사용자에 의해 강제로 중단되었습니다.")

    finally:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        data_filename = os.path.join(save_dir, f"collected_job_data_{timestamp}_{'completed' if completed_successfully else 'interrupted'}.json")
        error_filename = os.path.join(save_dir, f"job_error_log_{timestamp}.json")

        # 스크랩 데이터 저장
        with open(data_filename, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=4)

        # 에러 로그 저장
        if error_messages:
            with open(error_filename, 'w', encoding='utf-8') as f:
                json.dump(error_messages, f, ensure_ascii=False, indent=4)

        print(f"\n스크래핑 결과를 '{data_filename}' 파일로 저장했습니다.")
        if error_messages:
            print(f"오류 로그를 '{error_filename}' 파일로 저장했습니다.")
```

스크래핑 진행시 job_data, company_data 폴더를 생성하여 결과를 저장합니다.

page_number는 페이지 범위 입니다.

idx는 해당 페이지에서 스크래핑할 세부 인덱스입니다.

timeoutexception 등 오류가 생기면 해당 페이지, idx에서 오류가 발생했다고 표기하고 스크래핑을 진행합니다.

오류가 너무 많이 발생하거나 다른 이유로 강제종료시 그 동안 스크래핑한 데이터를 백업합니다.

