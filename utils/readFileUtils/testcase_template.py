"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : testcase_template.py
# @Date : 2022/7/19 11:40 上午
"""
from common.setting import ConfigHandler
from utils.readFileUtils.yamlControl import GetYamlData
import datetime
import os

'''用例模板'''


def write_case(case_path, page):
    with open(case_path, 'w', encoding='utf-8') as f:
        f.write(page)


def write_testcase_file(allure_epic, allure_feature, class_title,
                        func_title, case_path, yaml_path, file_name, allure_story):
    """

        :param allure_story:
        :param file_name: 文件名称
        :param allure_epic: 项目名称
        :param allure_feature: 模块名称
        :param class_title: 类名称
        :param func_title: 函数名称
        :param case_path: case 路径
        :param yaml_path: yaml 文件路径
        :return:
    """

    conf_data = GetYamlData(ConfigHandler.config_path).get_yaml_data()
    author = conf_data['TesterName']
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    real_time_update_test_cases = conf_data['real_time_update_test_cases']

    page = f'''#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : ${author}.py
# @Time : {now}        
    
    
import allure
import pytest
from common.setting import ConfigHandler
from utils.readFileUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.readFileUtils.regularControl import regular
from utils.requestsUtils.teardownControl import TearDownHandler


TestData = CaseData(ConfigHandler.data_path + r'{yaml_path}').case_process()
re_data = regular(str(TestData))


@allure.epic("{allure_epic}")
@allure.feature("{allure_feature}")
class Test{class_title}:

    @allure.story("{allure_story}")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_{func_title}(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl().http_request(in_data)
        TearDownHandler().teardown_handle(res)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'], status_code=res['status_code'])


if __name__ == '__main__':
    pytest.main(['{file_name}', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
'''
    if real_time_update_test_cases:
        write_case(case_path=case_path, page=page)
    elif real_time_update_test_cases is False:
        if not os.path.exists(case_path):
            write_case(case_path=case_path, page=page)

    else:
        raise  ValueError("real_time_update_test_cases 配置不正确，只能配置 True 或者 False")
