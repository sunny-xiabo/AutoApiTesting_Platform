"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : set_current_request_cache.py
# @Date : 2022/7/19 11:02 上午
"""

import jsonpath

from utils.cacheUtils.cacheControl import Cache


class SetCurrentRequestCache:

    def __init__(self, current_request_set_cache, request_data, response_data):
        self.current_request_set_cache = current_request_set_cache
        self.request_data = {"data": request_data}
        self.response_data = response_data

    def set_request_cache(self, jsonpath_value, cache_name):
        """将接口的请求参数存入缓存"""
        _request_data = jsonpath.jsonpath(self.request_data, jsonpath_value)
        if _request_data is False:
            raise ValueError("缓存设置失败，程序中未检测到需要缓存的数据。"
                             f"请求参数: {self.request_data}"
                             f"提取的 jsonpath 内容: {jsonpath_value}")
        else:
            Cache(cache_name).set_caches(_request_data[0])

    def set_response_cache(self, jsonpath_value, cache_name):
        """将响应结果存入缓存"""
        _response_data = jsonpath.jsonpath(self.response_data, jsonpath_value)
        if _response_data is False:
            raise ValueError("缓存设置失败，程序中未检测到需要缓存的数据。"
                             f"请求参数: {self.response_data}"
                             f"提取的 jsonpath 内容: {jsonpath_value}")
        else:
            Cache(cache_name).set_caches(_response_data[0])

    def set_caches_main(self):
        """设置缓存"""
        if self.current_request_set_cache is not None:
            for i in self.current_request_set_cache:
                _jsonpath = i['jsonpath']
                _cache_name = i['name']
                if i['type'] == 'request':
                    self.set_request_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
                elif i['type'] == 'response':
                    self.set_response_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
