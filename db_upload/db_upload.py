import subprocess
from logging_config import *

logger = logging.getLogger(script_name)


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
    "position.py"
    "job_position_mapping.py"
]

for script in scripts:
    print(f"{script} 실행")
    subprocess.run(["py", script, str(start_page), str(end_page)])

logger.info("모든 스크립트 실행 완료")
