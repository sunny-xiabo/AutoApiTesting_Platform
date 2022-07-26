"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : teardownControl.py
# @Date : 2022/7/19 11:50 上午
"""
from Enums.yamlData_enum import YAMLDate
from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.logControl import WARNING
from utils.sqlUtils.mysqlControl import MysqlDB
from utils.otherUtils.get_conf_data import sql_switch
from utils.otherUtils.jsonpath import jsonpath
from utils.otherUtils.jsonpath_date_replace import jsonpath_replace
from utils.readFileUtils.regularControl import sql_regular, cache_regular, regular
from utils.requestsUtils.requestControl import RequestControl

'''请求后置处理'''


class TearDownHandler:
    """ 处理yaml格式后置请求 """

    @classmethod
    def get_teardown_data(cls, case_data):
        return case_data[YAMLDate.TEARDOWN.value]

    @classmethod
    def get_response_data(cls, case_data):
        return case_data['response_data']

    @classmethod
    def get_teardown_sql(cls, case_data):
        return case_data[YAMLDate.TEARDOWN_SQL.value]

    @classmethod
    def jsonpath_replace_data(cls, replace_key, replace_value):
        # 通过jsonpath判断出需要替换数据的位置
        _change_data = replace_key.split(".")
        # jsonpath 数据解析
        _new_data = jsonpath_replace(change_data=_change_data, key_name='_teardown_case')
        if not isinstance(replace_value, str):
            _new_data += " = {0}".format(replace_value)
        # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
        else:
            _new_data += " = '{0}'".format(replace_value)
        return _new_data

    @classmethod
    def get_cache_name(cls, replace_key, resp_case_data):
        """
        获取缓存名称，并且讲提取到的数据写入缓存
        """
        if "$set_cache{" in replace_key and "}" in replace_key:
            start_index = replace_key.index("$set_cache{")
            end_index = replace_key.index("}", start_index)
            old_value = replace_key[start_index:end_index + 2]
            cache_name = old_value[11:old_value.index("}")]
            Cache(cache_name).set_caches(resp_case_data)

    @classmethod
    def regular_testcase(cls, teardown_case):
        """处理测试用例中的动态数据"""
        test_case = regular(str(teardown_case))
        test_case = eval(cache_regular(str(test_case)))
        return test_case

    @classmethod
    def teardown_http_requests(cls, teardown_case):
        """发送后置请求"""
        test_case = cls.regular_testcase(teardown_case)
        res = RequestControl().http_request(yaml_data=test_case, dependent_switch=False)
        return res

    def dependent_type_response(self, teardown_case_data, resp_data):
        """
        判断依赖类型为当前执行用例响应内容
        :param : teardown_case_data: teardown中的用例内容
        :param : resp_data: 需要替换的内容
        :return:
        """
        _replace_key = teardown_case_data['replace_key']
        _response_dependent = jsonpath(obj=resp_data, expr=teardown_case_data['jsonpath'])
        # 如果提取到数据，则进行下一步
        if _response_dependent is not False:
            _resp_case_data = _response_dependent[0]
            data = self.jsonpath_replace_data(replace_key=_replace_key, replace_value=_resp_case_data)
            self.jsonpath_replace_data(replace_key=_replace_key, replace_value=_resp_case_data)
        else:
            raise ValueError(f"jsonpath提取失败，替换内容: {resp_data} \n"
                             f"jsonpath: {teardown_case_data['jsonpath']}")
        return data

    def dependent_type_request(self, teardown_case_data, request_data):
        """
        判断依赖类型为请求内容
        :param : teardown_case_data: teardown中的用例内容
        :param : request_data: 需要替换的内容
        :return:
        """
        try:
            _request_set_value = teardown_case_data['set_value']
            _request_dependent = jsonpath(obj=request_data, expr=teardown_case_data['jsonpath'])
            if _request_dependent is not False:
                _request_case_data = _request_dependent[0]
                self.get_cache_name(replace_key=_request_set_value, resp_case_data=_request_case_data)
            else:
                raise ValueError(f"jsonpath提取失败，替换内容: {request_data} \n"
                                 f"jsonpath: {teardown_case_data['jsonpath']}")
        except KeyError:
            raise KeyError("teardown中缺少set_value参数，请检查用例是否正确")

    def dependent_self_response(self, teardown_case_data, res, resp_data):
        """
        判断依赖类型为依赖用例ID自己响应的内容
        :param : teardown_case_data: teardown中的用例内容
        :param : resp_data: 需要替换的内容
        :param : res: 接口响应的内容
        :return:
        """
        try:
            _set_value = teardown_case_data['set_cache']
            _response_dependent = jsonpath(obj=res['response_data'], expr=teardown_case_data['jsonpath'])
            # 如果提取到数据，则进行下一步
            if _response_dependent is not False:
                _resp_case_data = _response_dependent[0]
                # 拿到 set_cache 然后将数据写入缓存
                Cache(_set_value).set_caches(_resp_case_data)
                self.get_cache_name(replace_key=_set_value, resp_case_data=_resp_case_data)
            else:
                raise ValueError(f"jsonpath提取失败，替换内容: {resp_data} \n"
                                 f"jsonpath: {teardown_case_data['jsonpath']}")
        except KeyError:
            raise KeyError("teardown中缺少set_value参数，请检查用例是否正确")

    @classmethod
    def dependent_type_cache(cls, teardown_case):
        """
        判断依赖类型为从缓存中处理
        :param : teardown_case_data: teardown中的用例内容
        :return:
        """
        if teardown_case['dependent_type'] == 'cache':
            _cache_name = teardown_case['cache_data']
            _replace_key = teardown_case['replace_key']
            # 通过jsonpath判断出需要替换数据的位置
            _change_data = _replace_key.split(".")
            _new_data = jsonpath_replace(change_data=_change_data, key_name='_teardown_case')
            # jsonpath 数据解析
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in _cache_name for i in value_types) is True:
                _cache_data = Cache(_cache_name.split(':')[1]).get_cache()
                _new_data += " = {0}".format(_cache_data)

            # 最终提取到的数据,转换成 _teardown_case[xxx][xxx]
            else:
                _cache_data = Cache(_cache_name).get_cache()
                _new_data += " = '{0}'".format(_cache_data)

            return _new_data

    def teardown_handle(self, case_data):
        """ 后置处理逻辑 """
        # 拿到用例信息
        case_data = eval(cache_regular(str(case_data)))
        _teardown_data = self.get_teardown_data(case_data)
        # 获取接口的响应内容
        _resp_data = case_data['response_data']
        # 获取接口的请求参数
        _request_data = case_data['yaml_data']['data']
        # 判断如果没有 teardown
        if _teardown_data is not None:
            # 循环 teardown中的接口
            for _data in _teardown_data:
                if jsonpath(_data, '$.param_prepare') is not False:
                    _case_id = _data['case_id']
                    _teardown_case = eval(Cache('case_process').get_cache())[_case_id]
                    """
                    为什么在这里需要单独区分 param_prepare 和 send_request
                    假设此时我们有用例A，teardown中我们需要执行用例B

                    那么考虑用户可能需要获取获取teardown的用例B的响应内容，也有可能需要获取用例A的响应内容，
                    因此我们这里需要通过关键词去做区分。这里需要考虑到，假设我们需要拿到B用例的响应，那么就需要先发送请求然后在拿到响应数据

                    那如果我们需要拿到A接口的响应，此时我们就不需要在额外发送请求了，因此我们需要区分一个是前置准备param_prepare，
                    一个是发送请求send_request

                    """
                    _param_prepare = _data['param_prepare']
                    res = self.teardown_http_requests(_teardown_case)
                    for i in _param_prepare:
                        # 判断请求类型为自己,拿到当前case_id自己的响应
                        if i['dependent_type'] == 'self_response':
                            self.dependent_self_response(teardown_case_data=i, resp_data=_resp_data, res=res)

                        # # 判断从响应内容提取数据
                        # if i['dependent_type'] == 'response':
                        #     exec(self.dependent_type_response(teardown_case_data=i, resp_data=_resp_data))
                        #
                        # # 判断请求中的数据
                        # elif i['dependent_type'] == 'request':
                        #     self.dependent_type_request(teardown_case_data=i, request_data=_request_data)

                elif jsonpath(_data, '$.send_request') is not False:
                    _send_request = _data['send_request']
                    _case_id = _data['case_id']
                    _teardown_case = eval(Cache('case_process').get_cache())[_case_id]
                    for i in _send_request:
                        if i['dependent_type'] == 'cache':
                            exec(self.dependent_type_cache(teardown_case=i))
                        # 判断从响应内容提取数据
                        if i['dependent_type'] == 'response':
                            exec(self.dependent_type_response(teardown_case_data=i, resp_data=_resp_data))

                        # 判断请求中的数据
                        elif i['dependent_type'] == 'request':
                            self.dependent_type_request(teardown_case_data=i, request_data=_request_data)

                    test_case = self.regular_testcase(_teardown_case)
                    self.teardown_http_requests(test_case)
                self.teardown_sql(case_data)

    def teardown_sql(self, case_data):
        """处理后置sql"""
        sql_data = self.get_teardown_sql(case_data)
        _response_data = case_data['response_data']
        if sql_data is not None:
            for i in sql_data:
                if sql_switch():
                    _sql_data = sql_regular(value=i, res=_response_data)
                    print(_sql_data)
                    MysqlDB().execute(_sql_data)
                else:
                    WARNING.logger.warning(f"程序中检查到您数据库开关为关闭状态，已为您跳过删除sql: {i}")
