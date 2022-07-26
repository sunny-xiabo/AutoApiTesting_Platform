"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : jsonpath_date_replace.py
# @Date : 2022/7/18 6:25 下午
"""

def jsonpath_replace(change_data, key_name):
    """处理jsonpath数据"""
    _new_data = key_name + ''
    for i in change_data:
        if i == '$':
            pass
        elif i[0] == '[' and i[-1] == ']':
            _new_data += "[" + i[1:-1] + "]"
        else:
            _new_data += "[" + "'" + i + "'" + "]"
    return _new_data
