"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : logControl.py
# @Date : 2022/7/18 4:24 下午
"""

import logging
from common.setting import ConfigHandler
import colorlog
from logging import handlers


class LogHandler(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG,  # 最详细的日志信息，典型应用场景是问题诊断
        'info': logging.INFO,  # 信息详细程度仅次于DEBUG，通常只记录关键节点信息
        'error': logging.ERROR,  # 由于一个更严重的问题导致某些功能不能正常运行时记录的信息
        'warning': logging.WARNING,  # 当某些不期望的事情发生时记录的信息（如，磁盘可用空间较低），但是此时应用程序还是正常运行的
        'crit': logging.CRITICAL  # 当发生严重错误，导致运用程序不能继续运行时记录的信息
    }

    def __init__(self, filename, level='info', when='D', backCount=60, fmt="%(levelname)-8s%(asctime)s  "
                                                                           "%(name)s:%(filename)s:%(lineno)d %(message)s"):
        """
        初始化日志输出内容
        :param filename:
        :param level: CRITICAL 50 ERROR 40 WARNING 30 INFO 20 DEBUG 10 NOTSET 0
        :param when: S-Seconds M-Minutes H-Hours(默认) D-Days midnight-roll over at midnight W{0-6}-roll over on a certain day; 0-Monday
        :param backCount:
        :param fmt:
        """
        self.logger = logging.getLogger(filename)

        self.log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s 【%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=self.log_colors_config)

        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level))
        # 往屏幕上输出
        sh = logging.StreamHandler()
        # 设置屏幕上显示的格式
        sh.setFormatter(formatter)
        # 往文件里写入#指定间隔时间自动生成文件的处理器
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount, encoding='utf-8')
        """
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨    
        """
        # 设置文件里写入的格式
        th.setFormatter(format_str)
        # 把对象加到logger里
        self.logger.addHandler(sh)
        self.logger.addHandler(th)
        self.log_path = ConfigHandler.log_path


INFO = LogHandler(ConfigHandler.info_log_path, level='info')
ERROR = LogHandler(ConfigHandler.error_log_path, level='error')
WARNING = LogHandler(ConfigHandler.warning_log_path, level='warning')

if __name__ == '__main__':
    INFO.logger.info("测试info")
    ERROR.logger.error('测试error')
    WARNING.logger.warning('测试warning')
