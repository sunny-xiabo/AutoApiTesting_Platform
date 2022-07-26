"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : requestsUtils.py
# @Date : 2022/7/19 9:40 上午
"""
import copy
import os
import random
import time
import urllib

import jsonpath
import requests
from typing import Tuple, Dict
import urllib3
from utils.otherUtils.get_conf_data import sql_switch
from requests_toolbelt import MultipartEncoder
from utils.logUtils.logDecoratorl import log_decorator
from utils.sqlUtils.mysqlControl import MysqlDB
from utils.sqlUtils.postgresqlControl import PostgreDB
from Enums.requestType_enum import RequestType
from Enums.yamlData_enum import YAMLDate
from common.setting import ConfigHandler
from utils.logUtils.runTimeDecoratorl import execution_duration
from utils.otherUtils.allureData.allure_tools import allure_step, allure_step_no, allure_attach
from utils.readFileUtils.regularControl import cache_regular
from utils.requestsUtils.set_current_request_cache import SetCurrentRequestCache
from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.logControl import ERROR

# 忽略请求告警
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestControl:
    """封装请求"""

    @classmethod
    def _check_params(cls,
                      response: [str, dict],
                      yaml_data: Dict,
                      headers: Dict,
                      cookie: Dict,
                      res_time: float,
                      status_code: int,
                      teardown,
                      teardown_sql) -> Dict:
        _data = {
            "response_data": response,
            "sql_data": None,
            "yaml_data": yaml_data,
            "headers": headers,
            "cookie": cookie,
            "res_time": res_time,
            "status_code": status_code,
            "teardown": teardown,
            "teardown_sql": teardown_sql
        }
        """抽离通用模块，判断 http_request 方法中的一些数据校验"""
        # 判断数据库开关，开启状态，则返回对应的数据
        if sql_switch() and yaml_data['sql'] is not None:
            # sql_data = MysqlDB().assert_execution(
            #     sql=yaml_data['sql'],
            #     resp=response
            # )
            sql_data = PostgreDB().assert_execution(
                sql=yaml_data['sql'],
                resp=response
            )

            _data['sql_data'] = sql_data
        else:
            _data['response_data'] = response
            _data['sql_data'] = {'sql': None}

        return _data

    @classmethod
    def file_data_exit(
            cls,
            yaml_data: Dict,
            file_data) -> None:
        """判断上传文件时，data参数是否存在"""
        # 兼容又要上传文件，又要上传其他类型参数
        try:
            for key, value in yaml_data[YAMLDate.DATA.value]['data'].items():
                file_data[key] = value
        except KeyError:
            ...

    @classmethod
    def multipart_data(
            cls,
            file_data: Dict):
        multipart = MultipartEncoder(
            fields=file_data,  # 字典格式
            boundary='-----------------------------' + str(random.randint(int(1e28), int(1e29 - 1)))
        )
        return multipart

    @classmethod
    def check_headers_str_null(
            cls,
            headers: Dict) -> Dict:
        """
        兼容用户未填写headers或者header值为int
        @return:
        """
        headers = eval(cache_regular(str(headers)))
        if headers is None:
            return {"headers": None}
        else:
            for k, v in headers.items():
                if not isinstance(v, str):
                    headers[k] = str(v)
            return headers

    @classmethod
    def multipart_in_headers(
            cls,
            request_data: Dict,
            header: Dict) -> Tuple[dict, ...]:
        header = eval(cache_regular(str(header)))
        request_data = eval(cache_regular(str(request_data)))
        """ 判断处理header为 Content-Type: multipart/form-data"""
        if header is None:
            return request_data, {"headers": None}
        else:
            # 将header中的int转换成str
            for k, v in header.items():
                if not isinstance(v, str):
                    header[k] = str(v)
            if "multipart/form-data" in str(header.values()):
                # 判断请求参数不为空, 并且参数是字典类型
                if request_data and isinstance(request_data, dict):
                    # 当 Content-Type 为 "multipart/form-data"时，需要将数据类型转换成 str
                    for k, v in request_data.items():
                        if not isinstance(v, str):
                            request_data[k] = str(v)

                    request_data = MultipartEncoder(request_data)
                    header['Content-Type'] = request_data.content_type

        return request_data, header

    @classmethod
    def file_prams_exit(
            cls,
            yaml_data: Dict) -> Dict:
        """判断上传文件接口，文件参数是否存在"""
        try:
            params = yaml_data[YAMLDate.DATA.value]['params']
        except KeyError:
            params = None
        return params

    @classmethod
    def text_encode(
            cls,
            text: str) -> str:
        """unicode 解码"""
        return text.encode("utf-8").decode("utf-8")
        # return text

    @classmethod
    def response_elapsed_total_seconds(
            cls,
            res) -> float:
        """获取接口响应时长"""
        try:
            return res.elapsed.total_seconds() * 1000
        except AttributeError:
            return 0.00

    @classmethod
    def upload_file(
            cls,
            yaml_data: Dict) -> Tuple:
        """
        判断处理上传文件
        :param yaml_data:
        :return:
        """
        # 处理上传多个文件的情况
        yaml_data = eval(cache_regular(str(yaml_data)))
        _files = []
        file_data = {}
        # 兼容又要上传文件，又要上传其他类型参数
        cls.file_data_exit(yaml_data, file_data)
        for key, value in yaml_data[YAMLDate.DATA.value]['file'].items():
            file_path = ConfigHandler.file_path + value
            file_data[key] = (value, open(file_path, 'rb'), 'application/octet-stream')
            _files.append(file_data)
            # allure中展示该附件
            allure_attach(source=file_path, name=value, extension=value)
        multipart = cls.multipart_data(file_data)
        yaml_data[YAMLDate.HEADER.value]['Content-Type'] = multipart.content_type
        params_data = cls.file_prams_exit(yaml_data)
        return multipart, params_data, yaml_data

    @classmethod
    def get_response_cache(
            cls,
            response_cache: Dict,
            response_data: Dict,
            request_data: Dict) -> None:
        """
        将当前请求的接口存入缓存中
        @param response_cache: 设置缓存相关数据要求
        @param response_data: 接口相应内容
        @param request_data: 接口请求内容
        @return:
        """
        # 判断当前用例中如果有需要存入缓存的数据，才会进行下一步
        if response_cache is not None:
            _cache_name = response_cache['cache_name']
            _jsonpath = response_cache['jsonpath']
            _cache_type = response_cache['cache_type']
            _data = None
            if _cache_type == 'request':
                _data = jsonpath.jsonpath(
                    obj=request_data,
                    expr=_jsonpath
                )
            elif _cache_type == 'response':
                _data = jsonpath.jsonpath(
                    obj=response_data,
                    expr=_jsonpath
                )
            if _data is not False:
                Cache(_cache_name).set_caches(_data[0])
            else:
                ERROR.logger.error(f"缓存写入失败，接口返回数据 {response_cache} ，"
                                   f"接口请求数据 {request_data},"
                                   f"jsonpath内容：{response_cache}")

    def request_type_for_json(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: str,
            **kwargs) -> object:
        """ 判断请求类型为json格式 """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]

        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            json=_data,
            headers=_headers,
            verify=False,
            **kwargs
        )
        return res, _headers, _data, yaml_data

    def request_type_for_none(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: str,
            **kwargs) -> object:
        """判断 requestType 为 None"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        res = requests.request(
            method=method,
            url=yaml_data[YAMLDate.URL.value],
            data=None,
            headers=_headers,
            verify=False,
            **kwargs
        )
        return res, _headers, yaml_data

    def request_type_for_params(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: str,
            **kwargs) -> object:

        """处理 requestType 为 params """
        yaml_data = eval(cache_regular(str(yaml_data)))
        _data = yaml_data[YAMLDate.DATA.value]
        url = yaml_data[YAMLDate.URL.value]
        if _data is not None:
            # url 拼接的方式传参
            params_data = "?"
            for k, v in _data.items():
                if v is None or v == '':
                    params_data += (k + "&")
                else:
                    params_data += (k + "=" + str(v) + "&")
            url = yaml_data[YAMLDate.URL.value] + params_data[:-1]
        _headers = self.check_headers_str_null(headers)
        res = requests.request(method=method, url=url, headers=_headers, verify=False, **kwargs)
        return res, _data, url, _headers, yaml_data

    def request_type_for_file(
            self,
            yaml_data: Dict,
            method: str,
            **kwargs) -> object:
        """处理 requestType 为 file 类型"""
        multipart = self.upload_file(yaml_data)
        yaml_data = multipart[2]
        _headers = multipart[2][YAMLDate.HEADER.value]
        _headers = self.check_headers_str_null(_headers)
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value],
                               data=multipart[0], params=multipart[1], headers=_headers, verify=False, **kwargs)
        return res, _headers, yaml_data

    def request_type_for_data(
            self,
            yaml_data: Dict,
            data: Dict,
            headers: Dict,
            method: str,
            **kwargs) -> object:
        """判断 requestType 为 data 类型"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _data, _headers = self.multipart_in_headers(data, headers)
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value], data=_data, headers=_headers,
                               verify=False, **kwargs)
        return res, _data, _headers, yaml_data

    @classmethod
    def get_export_api_filename(cls, res):
        content_disposition = res.headers.get('content-disposition')
        filename_code = content_disposition.split("=")[-1]  # 分隔字符串，提取文件名
        filename = urllib.parse.unquote(filename_code)  # url解码
        return filename

    def request_type_for_export(
            self,
            yaml_data: Dict,
            headers: Dict,
            method: str,
            **kwargs):
        """判断 requestType 为 export 导出类型"""
        yaml_data = eval(cache_regular(str(yaml_data)))
        _headers = self.check_headers_str_null(headers)
        _data = yaml_data[YAMLDate.DATA.value]
        res = requests.request(method=method, url=yaml_data[YAMLDate.URL.value], json=_data, headers=_headers,
                               verify=False, stream=False, **kwargs)
        filepath = os.path.join(ConfigHandler.file_path, self.get_export_api_filename(res))  # 拼接路径
        if res.status_code == 200:
            if res.text:  # 判断文件内容是否为空
                with open(filepath, 'wb') as f:
                    for chunk in res.iter_content(chunk_size=1):  # iter_content循环读取信息写入，chunk_size设置文件大小
                        f.write(chunk)
            else:
                print("文件为空")

        return res, _data, _headers, yaml_data

    def api_allure_step(
            self,
            yaml_data: Dict,
            headers: str,
            method: str,
            data: str,
            dependent_data: str,
            assert_data: str,
            res,
    ) -> None:
        """ 在allure中记录请求数据 """
        _status_code = res.status_code
        allure_step_no(f"请求URL: {yaml_data[YAMLDate.URL.value]}")
        allure_step_no(f"请求方式: {method}")
        allure_step("请求头: ", headers)
        allure_step("请求数据: ", data)
        allure_step("依赖数据: ", dependent_data)
        allure_step("预期数据: ", assert_data)
        _res_time = self.response_elapsed_total_seconds(res)
        allure_step_no(f"响应耗时(ms): {_res_time}")

    @classmethod
    def get_res_cookie(cls, res) -> [bool, Dict]:
        """获取响应cookie"""
        try:
            cookie = res.cookies.get_dict()
        except:
            cookie = None
        return cookie

    def get_res_text(self, res, request_type):
        """兼容部分接口返回的内容为text文本内容"""
        try:
            res = res.json()
            allure_step("响应结果: ", res)
        except:
            # 判断当请求类型为导出类型的接口时，res 展示 文件名称
            if request_type == RequestType.EXPORT.value:
                res = self.get_export_api_filename(res)
            else:
                res = self.text_encode(res.text)
                allure_step("响应结果: ", res)
        return res

    @log_decorator(True)
    @execution_duration(3000)
    # @encryption("md5")
    def http_request(
            self,
            yaml_data: Dict,
            dependent_switch=True,
            **kwargs
    ):
        """
        请求封装
        :param yaml_data: 从yaml文件中读取出来的所有数据
        :param dependent_switch:
        :param kwargs:
        :return:
        """
        from utils.requestsUtils.dependentCase import DependentCase
        _is_run = yaml_data[YAMLDate.IS_RUN.value]
        _method = yaml_data[YAMLDate.METHOD.value]
        _detail = yaml_data[YAMLDate.DETAIL.value]
        _headers = yaml_data[YAMLDate.HEADER.value]
        _requestType = yaml_data[YAMLDate.REQUEST_TYPE.value].upper()
        _data = yaml_data[YAMLDate.DATA.value]
        _sql = yaml_data[YAMLDate.SQL.value]
        _assert = yaml_data[YAMLDate.ASSERT.value]
        _dependent_data = yaml_data[YAMLDate.DEPENDENCE_CASE_DATA.value]
        _teardown = yaml_data[YAMLDate.TEARDOWN.value]
        _teardown_sql = yaml_data[YAMLDate.TEARDOWN_SQL.value]
        _current_request_set_cache = yaml_data[YAMLDate.CURRENT_REQUEST_SET_CACHE.value]
        _sleep = yaml_data[YAMLDate.SLEEP.value]
        _response_cache = yaml_data[YAMLDate.RESPONSE_CACHE.value]
        res = None

        # 判断用例是否执行
        if _is_run is True or _is_run is None:
            # 处理多业务逻辑
            if dependent_switch is True:
                DependentCase().get_dependent_data(yaml_data)
            # 判断请求类型为json形式的
            if _requestType == RequestType.JSON.value:
                res, _headers, _data, yaml_data = self.request_type_for_json(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )
            elif _requestType == RequestType.NONE.value:
                res, _headers, yaml_data = self.request_type_for_none(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )

            elif _requestType == RequestType.PARAMS.value:
                res, _data, _url, _headers, yaml_data = self.request_type_for_params(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )
            # 判断上传文件
            elif _requestType == RequestType.FILE.value:
                res, _headers, yaml_data = self.request_type_for_file(
                    yaml_data=yaml_data,
                    method=_method,
                    **kwargs
                )

            elif _requestType == RequestType.DATA.value:
                res, _data, _headers, yaml_data = self.request_type_for_data(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    data=_data,
                    **kwargs
                )

            elif _requestType == RequestType.EXPORT.value:
                res, _data, _headers, yaml_data = self.request_type_for_export(
                    yaml_data=yaml_data,
                    headers=_headers,
                    method=_method,
                    **kwargs
                )
            # res 的值后期会被修改，复制一份，作用于部分函数的传参
            new_res = copy.deepcopy(res)
            if _sleep is not None:
                time.sleep(_sleep)
            self.api_allure_step(
                yaml_data=yaml_data,
                headers=_headers,
                method=_method,
                data=_data,
                dependent_data=_dependent_data,
                assert_data=_assert,
                res=new_res,
            )
            _status_code = res.status_code

            res = self.get_res_text(res=res, request_type=_requestType)

            # 将当前请求数据存入缓存中
            SetCurrentRequestCache(
                current_request_set_cache=_current_request_set_cache,
                request_data=yaml_data['data'],
                response_data=res
            ).set_caches_main()

            # 获取当前请求的缓存
            self.get_response_cache(
                response_cache=_response_cache,
                response_data=res,
                request_data=_data)
            _res_data = self._check_params(
                response=res,
                yaml_data=yaml_data,
                headers=_headers,
                cookie=self.get_res_cookie(new_res),
                res_time=self.response_elapsed_total_seconds(new_res),
                status_code=_status_code,
                teardown=_teardown,
                teardown_sql=_teardown_sql)
            return _res_data
        else:
            # 用例跳过执行的话，响应数据和sql数据为空
            _response_data = {
                "response_data": False,
                "sql_data": False,
                "yaml_data": yaml_data,
                "res_time": 0.00
            }
            return _response_data
