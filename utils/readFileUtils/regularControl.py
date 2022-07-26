"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : regularControl.py
# @Date : 2022/7/18 6:18 下午
"""

import json
import re
import datetime
import string

from faker import Faker
import random

from utils.cacheUtils.cacheControl import Cache
from utils.logUtils.logControl import ERROR
from utils.otherUtils.jsonpath import jsonpath

'''自定义函数调用'''


class Context:
    def __init__(self):
        self.f = Faker(locale='zh_CN')

    def get_phone(self) -> int:
        """
        :return: 随机生成手机号码
        """
        phone = self.f.phone_number()
        return phone

    def get_job(self) -> str:
        """
        :return: 随机生成职业
        """

        job = self.f.job()
        return job

    def get_id_number(self) -> int:
        """
        :return: 随机生成身份证号码
        """

        id_number = self.f.ssn()
        return id_number

    def get_female_name(self) -> str:
        """
        :return: 女生姓名
        """
        female_name = self.f.name_female()
        return female_name

    def get_male_name(self) -> str:
        """
        :return: 男生姓名
        """
        male_name = self.f.name_male()
        return male_name

    def get_email(self) -> str:
        """
        :return: 生成邮箱
        """
        email = self.f.email()
        return email

    def get_country(self):
        """
        @return: 生成国家
        """
        country = self.f.country()
        return country

    def get_element(self):
        """
        @return: 生成随机字母
        """
        element = self.f.random_element()
        return element

    def get_scope_num(self):
        """
        获取范围数 1，2，3
        @return:
        """
        scope_num_list = [1, 2, 3]
        scope_num = random.choice(scope_num_list)
        return scope_num

    def get_unit(self):
        """
        获取计量单位
        @return:
        """
        unit_list = ['m', 'kg）', 's', 'A', 'K', 'mol', 'cd', 'rad', 'sr', 'Hz', 'N', 'Pa', 'J', 'W', 'C', 'V', 'F', 'Ω',
                     'S', 'Wb', 'T', 'H', '℃', 'lm', 'lx', 'Bq', 'Gy', 'Sv', 'min', 'h', 'd', 'r/min', 'n/mile', 'kn',
                     't', 'u', 'L', 'eV', 'dB', 'tex']
        nuit_choice = random.choice(unit_list)
        return nuit_choice

    def get_pyfloat(self):
        """
        生成随机整数、小数、只有整数数字
        left_digits=1,  生成整数位数
        right_digits=2, 生成小数位数
        positive=True 是否只有整数 True 显示正数 False 显示负数
        @return:
        """
        pyfloat = self.f.pyfloat(left_digits=1, right_digits=2, positive=True)
        return pyfloat

    def get_punc(self):
        """
        @return: 返回特殊字符
        """
        puc = "!$%&()*+"
        return puc


    @classmethod
    def get_time(cls) -> str:
        """
        计算当前时间
        :return:
        """
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    def random_int(self):
        """随机生成 0 - 9999 的数字"""
        numbers = self.f.random_int()
        return numbers

    @classmethod
    def host(cls) -> str:
        from utils.readFileUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['host']
        return host

    @classmethod
    def app_host(cls) -> str:
        """获取app的host"""
        from utils.readFileUtils.yamlControl import GetYamlData
        from common.setting import ConfigHandler

        # 从配置文件conf.yaml 文件中获取到域名，然后使用正则替换
        host = GetYamlData(ConfigHandler.config_path) \
            .get_yaml_data()['app_host']
        return host


def sql_json(js_path, res):
    return jsonpath(res, js_path)[0]


def regular(target):
    """
    新版本
    使用正则替换请求数据
    :return:
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(":")[1].split("(")[0]
                value_name = key.split(":")[1].split("(")[1][:-1]
                value_data = getattr(Context(), func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_pattern, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error("未找到对应的替换的数据, 请检查数据是否正确", target)
        raise


def sql_regular(value, res=None):
    """
    这里处理sql中的依赖数据，通过获取接口响应的jsonpath的值进行替换
    :param res: jsonpath使用的返回结果
    :param value:
    :return:
    """
    sql_json_list = re.findall(r"\$json\((.*?)\)\$", value)

    for i in sql_json_list:
        pattern = re.compile(r'\$json\(' + i.replace('$', "\$").replace('[', '\[') + r'\)\$')
        key = str(sql_json(i, res))
        value = re.sub(pattern, key, value, count=1)

    return value


def cache_regular(value):
    """
    通过正则的方式，读取缓存中的内容
    例：$cache{login_init}
    :param value:
    :return:
    """
    # 正则获取 $cache{login_init}中的值 --> login_init
    regular_dates = re.findall(r"\$cache\{(.*?)\}", value)

    # 拿到的是一个list，循环数据
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        if any(i in regular_data for i in value_types) is True:
            value_types = regular_data.split(":")[0]
            regular_data = regular_data.split(":")[1]
            pattern = re.compile(r'\'\$cache{' + value_types.split(":")[0] + r'(.*?)}\'')
        else:
            pattern = re.compile(r'\$cache\{' + regular_data.replace('$', "\$").replace('[', '\[') + r'\}')
        cache_data = Cache(regular_data).get_cache()
        # 使用sub方法，替换已经拿到的内容
        value = re.sub(pattern, cache_data, value)
    return value


# c = Context()
# print(c.get_punc())


