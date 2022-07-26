"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : setting.py
# @Date : 2022/7/18 3:57 下午
"""

import os

'''路径配置存放类'''


class ConfigHandler:
    # os.sep 根据所处的平台，自动采用相应的分隔符号
    _SLASH = os.sep
    # 项目路径
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 用例路径
    case_path = os.path.join(root_path, 'test_cases' + _SLASH)

    # 测试用例数据路径
    data_path = os.path.join(root_path, 'data' + _SLASH)

    # 缓存cache路径
    cache_path = os.path.join(root_path, 'Cache' + _SLASH)
    if not os.path.exists(cache_path):
        os.mkdir(cache_path)
    # 日志存储路径
    log_path = os.path.join(root_path, 'logs' + _SLASH + 'log.log')
    # info日志存储路径
    info_log_path = os.path.join(root_path, 'logs' + _SLASH + 'info.log')
    # error日志存储路径
    error_log_path = os.path.join(root_path, 'logs' + _SLASH + 'error.log')
    # warning日志存储路径
    warning_log_path = os.path.join(root_path, 'logs' + _SLASH + 'warning.log')
    # 共享目录路径
    common_path = os.path.join(root_path, 'common' + _SLASH)
    # 配置路径
    config_path = os.path.join(root_path, 'common' + _SLASH + 'conf.yaml')
    # 文件存储路径
    file_path = os.path.join(root_path, 'Files' + _SLASH)
    # 工具路径
    util_path = os.path.join(root_path, 'utils' + _SLASH)

    util_install_path = util_path + 'otherUtils' + _SLASH + 'InstallUtils' + _SLASH

    # 测试报告路径
    report_path = os.path.join(root_path, 'reports')
    # 测试报告中的test_case路径
    report_html_test_case_path = os.path.join(root_path, 'reports' + _SLASH +
                                              "html" + _SLASH + 'data' + _SLASH + "test-cases" + _SLASH)

    # 测试报告中的attachments路径
    report_html_attachments_path = os.path.join(root_path, 'reports' + _SLASH +
                                                "html" + _SLASH + 'data' + _SLASH + "attachments" + _SLASH)

    excel_template = os.path.join(root_path, 'utils' + _SLASH + 'otherUtils' + _SLASH + "allureData" + _SLASH)


if __name__ == '__main__':
    print(ConfigHandler.report_html_test_case_path)
