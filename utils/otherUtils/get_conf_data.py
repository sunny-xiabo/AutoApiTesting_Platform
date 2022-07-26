"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : get_conf_data.py
# @Date : 2022/7/18 6:08 下午
"""

from common.setting import ConfigHandler
from utils.readFileUtils.yamlControl import GetYamlData

conf = GetYamlData(ConfigHandler.config_path).get_yaml_data()


def sql_switch():
    '''获取数据开关
        根据数据库类型选择返回的值
    '''

    switch_mysql = conf['MySqlDB']['switch']
    switch_postgresql = conf['PostgreDB']['switch']
    return switch_postgresql


def get_notification_type():
    """
    获取报告通知类型，钉钉/企微/飞书
    :return:
    """
    date = conf['NotificationType']
    return date


def get_excel_report_switch():
    """获取excel报告开关"""
    excel_report_switch = conf['excel_report']
    return excel_report_switch


def get_mirror_url():
    """获取镜像源"""
    mirror_url = conf['mirror_source']
    return mirror_url


project_name = conf['ProjectName'][0]
tester_name = conf['TesterName']

if __name__ == '__main__':
    print(conf['MySqlDB']['switch'])
