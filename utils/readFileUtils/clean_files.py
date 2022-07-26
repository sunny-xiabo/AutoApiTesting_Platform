"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : clean_files.py
# @Date : 2022/7/18 5:32 下午
"""

import os


def del_file(path):
    """
    删除目录下的文件
    :param path:
    :return:
    """
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
