"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : yamlControl.py
# @Date : 2022/7/18 5:09 下午
"""

import os
import yaml.scanner

from utils.readFileUtils.regularControl import regular

'''获取yaml数据类'''


class GetYamlData:

    def __init__(self, file_dir):
        self.fileDir = file_dir

    def get_yaml_data(self) -> dict:
        """
        获取 yaml 中的数据
        :param: fileDir:
        :return:
        """
        # 判断文件是否存在
        if os.path.exists(self.fileDir):
            data = open(self.fileDir, 'r', encoding='utf-8')
            try:
                res = yaml.load(data, Loader=yaml.FullLoader)
                return res
            except Exception as e:
                _error_msg = str(e).split(",")
                _file_path = _error_msg[0].split("in")[-1]
                _error_line = _error_msg[1]

                raise ValueError("yaml格式不正确, 请检查下方对应路径中的文件内容, 文件路径: {}, 错误行号：{}"
                                 .format(_file_path, _error_line))

        else:
            raise FileNotFoundError("文件路径不存在")

    def write_yaml_data(self, key: str, value) -> int:
        """
        更改 yaml 文件中的值
        :param key: 字典的key
        :param value: 写入的值
        :return:
        """
        with open(self.fileDir, 'r', encoding='utf-8') as f:
            # 创建了一个空列表，里面没有元素
            lines = []
            for line in f.readlines():
                if line != '\n':
                    lines.append(line)
            f.close()

        with open(self.fileDir, 'w', encoding='utf-8') as f:
            flag = 0
            for line in lines:
                left_str = line.split(":")[0]
                if key == left_str and '#' not in line:
                    newline = "{0}: {1}".format(left_str, value)
                    line = newline
                    f.write('%s\n' % line)
                    flag = 1
                else:
                    f.write('%s' % line)
            f.close()
            return flag


class GetCaseData(GetYamlData):

    def get_different_formats_yaml_data(self) -> list:
        """
        获取兼容不同格式的yaml数据
        :return:
        """
        res_list = []
        for i in self.get_yaml_data():
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """
        获取测试用例数据, 转换成指定数据格式
        :return:
        """

        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = regular(str(_yaml_data))
        return eval(re_data)



if __name__ == '__main__':
    g = GetYamlData('/Users/xiabo/SoftwareTest/carbonPy/AutoApi_Platform/data/CLTEmissionScource/clt_add_EmissionSource.yaml')
    print(g.get_yaml_data())
