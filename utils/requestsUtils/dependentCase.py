"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : dependentCase.py
# @Date : 2022/7/19 10:45 上午
"""
from Enums.dependentType_enum import DependentType
from Enums.yamlData_enum import YAMLDate
from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.logControl import WARNING
from utils.sqlUtils.mysqlControl import MysqlDB
from utils.sqlUtils.postgresqlControl import PostgreDB
from utils.otherUtils.get_conf_data import sql_switch
from utils.otherUtils.jsonpath import jsonpath
from utils.otherUtils.jsonpath_date_replace import jsonpath_replace
from utils.readFileUtils.regularControl import regular, cache_regular
from utils.requestsUtils.requestControl import RequestControl


class DependentCase:

    @classmethod
    def get_cache(cls, case_id: str) -> dict:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id:
        :return: case_id_01
        """
        _case_data = eval(Cache('case_process').get_cache())[case_id]
        return _case_data

    @classmethod
    def jsonpath_data(cls, obj: dict, expr: str) -> list:
        """
        通过jsonpath提取依赖的数据
        :param obj: 对象信息
        :param expr: jsonpath 方法
        :return: 提取到的内容值,返回是个数组

        对象: {"data": applyID} --> jsonpath提取方法: $.data.data.[0].applyId
        """

        _jsonpath_data = jsonpath(obj, expr)
        # 判断是否正常提取到数据，如未提取到，则抛异常
        if _jsonpath_data is not False:
            return _jsonpath_data
        else:
            raise ValueError(f"jsonpath提取失败！\n 提取的数据: {obj} \n jsonpath规则: {expr}")

    @classmethod
    def set_cache_value(cls, dependent_data):
        """
        获取依赖中是否需要将数据存入缓存中
        """
        try:
            return dependent_data['set_cache']
        except KeyError:
            return None

    @classmethod
    def replace_key(cls, dependent_data):
        try:
            _replace_key = dependent_data[YAMLDate.REPLACE_KEY.value]
            return _replace_key
        except KeyError:
            return None

    @classmethod
    def url_replace(cls, replace_key: str, jsonpath_dates: dict, jsonpath_data: list, case_data: dict):
        """
        url中的动态参数替换
        # 如: 一般有些接口的参数在url中,并且没有参数名称, /api/v1/work/spu/approval/spuApplyDetails/{id}
        # 那么可以使用如下方式编写用例, 可以使用 $url_params{}替换,
        # 如/api/v1/work/spu/approval/spuApplyDetails/$url_params{id}
        :param jsonpath_data: jsonpath 解析出来的数据值
        :param replace_key: 用例中需要替换数据的 replace_key
        :param jsonpath_dates: jsonpath 存放的数据值
        :param case_data: 用例数据
        :return:
        """

        if "$url_param" in replace_key:
            _url = case_data['url'].replace(replace_key, str(jsonpath_data[0]))
            jsonpath_dates['$.url'] = _url
        else:
            jsonpath_dates[replace_key] = jsonpath_data[0]

    @classmethod
    def _dependent_type_for_sql(cls, setup_sql, dependence_case_data, jsonpath_dates, case_data):
        """
        判断依赖类型为 sql，程序中的依赖参数从 数据库中提取数据
        @param setup_sql: 前置sql语句
        @param dependence_case_data: 依赖的数据
        @param jsonpath_dates: 依赖相关的用例数据
        @param case_data:
        @return:
        """
        # 判断依赖数据类型，依赖 sql中的数据
        if setup_sql is not None:
            if sql_switch():
                # sql_data = MysqlDB().setup_sql_data(sql=setup_sql)
                sql_data = PostgreDB().setup_sql_data(sql=setup_sql)
                dependent_data = dependence_case_data['dependent_data']
                for i in dependent_data:
                    _jsonpath = i[YAMLDate.JSONPATH.value]
                    jsonpath_data = cls.jsonpath_data(obj=sql_data, expr=_jsonpath)
                    _set_value = cls.set_cache_value(i)
                    _replace_key = cls.replace_key(i)
                    if _set_value is not None:
                        Cache(_set_value).set_caches(jsonpath_data[0])
                    if _replace_key is not None:
                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                        jsonpath_data=jsonpath_data, case_data=case_data)
            else:
                WARNING.logger.warning("检查到数据库开关为关闭状态，请确认配置")

    @classmethod
    def is_dependent(cls, case_data: dict) -> [list, bool]:
        """
        判断是否有数据依赖
        :return:
        """

        # 获取用例中的dependent_type值，判断该用例是否需要执行依赖
        _dependent_type = case_data[YAMLDate.DEPENDENCE_CASE.value]
        # 获取依赖用例数据
        _dependence_case_dates = case_data[YAMLDate.DEPENDENCE_CASE_DATA.value]
        _setup_sql = case_data[YAMLDate.SETUP_SQL.value]
        # 判断是否有依赖
        if _dependent_type is True:
            # 读取依赖相关的用例数据
            jsonpath_dates = {}
            # 循环所有需要依赖的数据
            try:

                for dependence_case_data in _dependence_case_dates:

                    _case_id = dependence_case_data[YAMLDate.CASE_ID.value]
                    # 判断依赖数据为sql，case_id需要写成self，否则程序中无法获取case_id
                    if _case_id == 'self':
                        cls._dependent_type_for_sql(setup_sql=_setup_sql, dependence_case_data=dependence_case_data,
                                                    jsonpath_dates=jsonpath_dates, case_data=case_data)
                    else:
                        re_data = regular(str(cls.get_cache(_case_id)))
                        re_data = eval(cache_regular(str(re_data)))
                        res = RequestControl().http_request(re_data)
                        if jsonpath(obj=dependence_case_data, expr="$.dependent_data") is not False:
                            dependent_data = dependence_case_data['dependent_data']
                            for i in dependent_data:

                                _case_id = dependence_case_data[YAMLDate.CASE_ID.value]
                                _jsonpath = i[YAMLDate.JSONPATH.value]
                                _request_data = case_data[YAMLDate.DATA.value]
                                _replace_key = cls.replace_key(i)
                                _set_value = cls.set_cache_value(i)
                                # 判断依赖数据类型, 依赖 response 中的数据
                                if i[YAMLDate.DEPENDENT_TYPE.value] == DependentType.RESPONSE.value:
                                    jsonpath_data = cls.jsonpath_data(res['response_data'], _jsonpath)
                                    if _set_value is not None:
                                        Cache(_set_value).set_caches(jsonpath_data[0])
                                    if _replace_key is not None:
                                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                                        jsonpath_data=jsonpath_data, case_data=case_data)

                                # 判断依赖数据类型, 依赖 request 中的数据
                                elif i[YAMLDate.DEPENDENT_TYPE.value] == DependentType.REQUEST.value:
                                    jsonpath_data = cls.jsonpath_data(res['yaml_data']['data'], _jsonpath)
                                    if _set_value is not None:
                                        Cache(_set_value).set_caches(jsonpath_data[0])
                                    if _replace_key is not None:
                                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                                        cls.url_replace(replace_key=_replace_key, jsonpath_dates=jsonpath_dates,
                                                        jsonpath_data=jsonpath_data, case_data=case_data)
                                    else:
                                        raise ValueError("当前用例需要获取sql数据，setup_sql中需要填写对应的sql语句。\n"
                                                         "case_id: {0}".format(_case_id))
                                else:
                                    raise ValueError("依赖的dependent_type不正确，只支持request、response、sql依赖\n"
                                                     f"当前填写内容: {i[YAMLDate.DEPENDENT_TYPE.value]}")
                return jsonpath_dates
            except KeyError as e:
                raise KeyError(f"dependence_case_data依赖用例中，未找到 {e} 参数，请检查是否填写"
                               f"如已填写，请检查是否存在yaml缩进问题")
            except TypeError:
                raise TypeError("dependence_case_data下的所有内容均不能为空！请检查相关数据是否填写，如已填写，请检查缩进问题")

        else:
            return False

    @classmethod
    def get_dependent_data(cls, yaml_data: dict) -> None:
        """
        jsonpath 和 依赖的数据,进行替换
        :param yaml_data:
        :return:
        """
        _dependent_data = DependentCase().is_dependent(yaml_data)
        # 判断有依赖
        if _dependent_data is not None and _dependent_data is not False:
            # if _dependent_data is not False:
            for key, value in _dependent_data.items():
                # 通过jsonpath判断出需要替换数据的位置
                _change_data = key.split(".")
                # jsonpath 数据解析
                _new_data = jsonpath_replace(change_data=_change_data, key_name='yaml_data')
                # 最终提取到的数据,转换成 yaml_data[xxx][xxx]
                _new_data += ' = value'
                exec(_new_data)
