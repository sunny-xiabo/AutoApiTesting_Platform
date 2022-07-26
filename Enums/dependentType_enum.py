"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : dependentType_enum.py
 # @Date ：2022/7/18 22:15
"""


from enum import Enum, unique


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """
    # 依赖响应中数据
    RESPONSE = 'response'
    # 依赖请求中的数据
    REQUEST = 'request'
    # 依赖sql中的数据
    SQL_DATA = 'sqlData'
    # 依赖存入缓存中的数据
    CACHE = "cache"
