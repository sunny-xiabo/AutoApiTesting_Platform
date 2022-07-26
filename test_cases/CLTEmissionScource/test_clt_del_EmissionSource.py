#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : $Summer.py
# @Time : 2022-07-26 10:33:36        
    
    
import allure
import pytest
from common.setting import ConfigHandler
from utils.readFileUtils.get_yaml_data_analysis import CaseData
from utils.assertUtils.assertControl import Assert
from utils.requestsUtils.requestControl import RequestControl
from utils.readFileUtils.regularControl import regular
from utils.requestsUtils.teardownControl import TearDownHandler


TestData = CaseData(ConfigHandler.data_path + r'CLTEmissionScource/clt_del_EmissionSource.yaml').case_process()
re_data = regular(str(TestData))


@allure.epic("Carbon Lens TEC")
@allure.feature("排放源管理模块")
class TestCltDelEmissionsource:

    @allure.story("排放源删除接口")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_clt_del_EmissionSource(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl().http_request(in_data)
        TearDownHandler().teardown_handle(res)
        Assert(in_data['assert']).assert_equality(response_data=res['response_data'], 
                                                  sql_data=res['sql_data'], status_code=res['status_code'])


if __name__ == '__main__':
    pytest.main(['test_clt_del_EmissionSource.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])