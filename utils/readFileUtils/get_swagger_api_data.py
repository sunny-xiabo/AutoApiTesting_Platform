"""
 # -*- coding:utf-8 -*-
 # @Author：summer
 # @File : get_swagger_api_data.py
 # @Date ：2022/7/27 11:38 上午
 # Explain: 文件说明
"""

import json

import requests

from common.setting import ConfigHandler
from utils.logUtils.logControl import INFO, ERROR
from utils.otherUtils.get_conf_data import get_swagger_url


# TODO: 从swagger导出JSON文件，转成yaml格式的测试用例
class SwaggerApiJson:
    """获取swagger中的api数据，转化成yaml"""

    def __init__(self):
        self.file_path = ConfigHandler.file_path + 'data.json'
        self.case_id_num = 0
        self.res = requests.get(get_swagger_url()).json()

    def write_swagger_data(self):
        """
        获取swagger数据存储至文件
        @return:
        """
        res = self.res
        if isinstance(res, dict):
            with open(ConfigHandler.file_path + 'data.json', 'w', encoding='utf-8') as f:
                json.dump(res, f, indent=4, ensure_ascii=False)

    def check_data(self):
        """检查返回的数据是否dict"""
        if not isinstance(self.res, dict):
            ERROR.logger.error("返回的数据不是dict,请检查")
            return False
        else:
            INFO.logger.info("返回的数据是dict")
            return True

    def get_api_json(self):
        """
        获取JSON文件中的数据
        @return:
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['paths']

    def get_case_id(self, url):
        """
        根据请求url, 生成 yaml 用例中的 case_id
        :param url: /system/user/authRole
        :return: authRole_1
        """
        case_name = url.split("/")[-1]
        case_id = case_name + "_" + str(self.case_id_num)
        self.case_id_num += 1
        return case_id

    @classmethod
    def get_url(cls, json_data):
        """
        获取请求 path
        :param json_data:
        :return:
        """
        return json_data

    def get_detail(self):
        pass

    @classmethod
    def get_request_body(cls, json_data):
        request_type = 'JSON'
        """获取请求参数内容"""
        if 'requestBody' in json_data:
            request_type = 'JSON'
            return json_data['requestBody'], request_type
        elif 'parameters' in json_data:
            request_type = 'PARAMS', request_type
            return json_data['parameters'], request_type
        else:
            return None, request_type

    def get_headers(self, json_data):
        """获取请求头"""
        pass

    def get_host(self):
        """获取host"""
        yaml_data = {}
        api_json = self.get_api_json()
        for k, v in api_json.items():
            case_id = self.get_case_id(k)
            yaml_data[case_id] = {}
            yaml_data[case_id]['url'] = k
            for key, value in v.items():
                yaml_data[case_id]['method'] = key
                yaml_data[case_id]['detail'] = value['summary']
                yaml_data[case_id]['data'] = self.get_request_body(value)[0]
                yaml_data[case_id]['requestType'] = self.get_request_body([1])
                yaml_data[case_id]['headers'] = '1'
                # print(key, value)
        print(yaml_data)


if __name__ == '__main__':
    SwaggerApiJson().write_swagger_data()
    SwaggerApiJson().check_data()
    print(SwaggerApiJson().get_api_json())
    SwaggerApiJson().get_host()

