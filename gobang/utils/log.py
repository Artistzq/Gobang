"""
问题1：无法多进程使用，文件被占用
问题2：不是单例，导致重复的日志出现
"""

import logging
from logging import handlers
import time

path = "../../logs/gobang.log"


class Logger(object):

    def __init__(self, filename="", level='DEBUG', when='D', back_count=3,
                 fmt='%(levelname)s: %(message)s '
                     '-%(asctime)s-[PID:%(process)d]-[TID:%(thread)d]'
                     '-%(filename)s[line:%(lineno)d]'
                     '-%(module)s-%(funcName)s', logger_name=None):
        """
        :param filename: 日志文件位置
        :param level: DEBUG, INFO, WARNING, ERROR, CRITIC 五个最低等级
        :param when: 备份频率：天（day）
        :param back_count: 备份数量
        :param fmt: 格式
        :param logger_name: logger的name
        """
        if filename == "":
            localtime = time.asctime(time.localtime(time.time()))
            filename = ("../logs/" + "-".join(localtime.split()) + ".log").replace(":", "_")
        self.logger = logging.getLogger(logger_name)  # 根据文件名创建一个日志
        self.logger.setLevel(level)  # 设置默认日志级别
        self.format_str = logging.Formatter(fmt)  # 设置日志格式

        if not self.logger.handlers:
            # 如果有handler，就不再添加了，避免重复
            screen_handler = logging.StreamHandler()  # 屏幕输出处理器
            screen_handler.setFormatter(self.format_str)  # 设置屏幕输出显示格式

            # 定时写入文件处理器
            time_file_handler = handlers.TimedRotatingFileHandler(filename=filename,  # 日志文件名
                                                                  when=when,  # 多久创建一个新文件
                                                                  interval=1,  # 写入时间间隔
                                                                  backupCount=back_count,  # 备份文件的个数
                                                                  encoding='utf-8')  # 编码格式

            time_file_handler.setFormatter(self.format_str)

            # 添加日志处理器
            self.logger.addHandler(screen_handler)
            self.logger.addHandler(time_file_handler)

    def get_logger(self):
        """
        返回此logger
        :return:
        """
        return self.logger


if __name__ == '__main__':
    logger = Logger("../../logs/gobang.log").get_logger()
    logger.debug("test")
