"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : allure_tools.py
 # @Date ：2022/7/18 21:58
"""

import allure
import json

from Enums.AllureAttachmentType_enum import AllureAttachmentType


def allure_step(step, var):
    """
    allur 步骤
    :param step: 步骤及附件名称
    :param var: 附件内容
    :return:
    """
    with allure.step(step):
        allure.attach(
            json.dumps(
                str(var),
                ensure_ascii=False,
                indent=4),
            step, allure.attachment_type.JSON)


def allure_attach(source, name, extension):
    """
    allure 报告上传附件、图片、Excel等
    :param source: 文件路径，相当于传一个文件
    :param name: 附件名称
    :param extension: 附件的扩展名称
    :return:
    """
    # 获取上传附件的尾缀，判断对应的 attachment_type 枚举值
    _NAME = name.split('.')[-1].upper()
    _attachment_type = getattr(AllureAttachmentType, _NAME, None)

    allure.attach.file(source=source, name=name,
                       attachment_type=_attachment_type if _attachment_type is None else _attachment_type.value,
                       extension=extension)


def allure_step_no(step):
    """
    无附件的操作步骤
    :param step: 步骤名称
    :return:
    """
    with allure.step(step):
        pass
