"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : yamlData_enum.py
 # @Date ：2022/7/18 22:09
"""

from enum import Enum


class YAMLDate(Enum):
    """
    测试用例相关字段
    """
    # host 配置
    HOST = 'host'
    # 接口请求的url
    URL = 'url'
    # 请求方式
    METHOD = 'method'
    # 请求头
    HEADER = 'headers'
    # 请求类型
    REQUEST_TYPE = 'requestType'
    # 是否执行
    IS_RUN = 'is_run'
    # 请求参数
    DATA = 'data'
    # 是否依赖用例
    DEPENDENCE_CASE = 'dependence_case'
    # 依赖用例参数
    DEPENDENCE_CASE_DATA = 'dependence_case_data'
    # 断言内容
    ASSERT = 'assert'
    # sql内容
    SQL = 'sql'
    # 用例ID
    CASE_ID = 'case_id'
    # jsonpath提取
    JSONPATH = 'jsonpath'
    # 替换的内容
    REPLACE_KEY = 'replace_key'
    # 依赖数据类型
    DEPENDENT_TYPE = 'dependent_type'
    # 用例描述
    DETAIL = 'detail'
    # 前置sql
    SETUP_SQL = 'setup_sql'
    STATUS_CODE = "status_code"
    TEARDOWN = "teardown"
    TEARDOWN_SQL = 'teardown_sql'
    # 当前请求用例设置缓存
    CURRENT_REQUEST_SET_CACHE = "current_request_set_cache"

    # 设置等待时间
    SLEEP = 'sleep'

    # 缓存数据存放
    RESPONSE_CACHE = 'response_cache'
