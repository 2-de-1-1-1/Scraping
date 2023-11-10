import logging
import os

script_name = os.path.basename(__file__)

logger = logging.getLogger(script_name)

log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

log_handler = logging.FileHandler('script_log.log', encoding='utf-8')
log_handler.setFormatter(log_formatter)

logger.setLevel(logging.INFO)

logger.addHandler(log_handler)


class NoModuleFilter(logging.Filter):
    def filter(self, record):
        record.filename = os.path.basename(record.filename)
        return True


logger.addFilter(NoModuleFilter())

logger.info('모든 페이지 작업 완료')
