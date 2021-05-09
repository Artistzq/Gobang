import sys
import os

# print(sys.path[0])
# print(os.path.split(sys.path[0]))

# abspath = os.path.abspath(__file__)
# pj_dir = os.path.split(os.path.split(os.path.split(abspath)[0])[0])[0]
# log_dir = os.path.join(pj_dir, "logs\\abs.log")
# print(log_dir)

from gobang.utils import log

# print(log.path)
# # log.path = "aaa.log"
# print(log.path)

logger = log.Logger(filename=log.path, logger_name=__name__).get_logger()
print(log.path)
logger.info("sss")