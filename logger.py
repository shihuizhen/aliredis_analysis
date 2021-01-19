import logging
import logging.config
from settings import logging_conf

logging.config.dictConfig(logging_conf)
app_logger = logging.getLogger("dingding")

# if __name__ == "__main__":
#     app_logger.error("logger error",exc_info = True) 
#     app_logger.info("logger info")
