"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : requestType_enum.py
 # @Date ：2022/7/18 22:12
"""

from enum import Enum


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    # json 类型
    JSON = "JSON"
    # PARAMS 类型
    PARAMS = "PARAMS"
    # data 类型
    DATA = "DATA"
    # 文件类型
    FILE = 'FILE'
    # 导出文件
    EXPORT = "EXPORT"
    # 没有请求参数
    NONE = "NONE"
