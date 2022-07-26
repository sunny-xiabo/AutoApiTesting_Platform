"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : notificationType_enum.py
 # @Date ：2022/7/18 22:13
"""


from enum import Enum


class NotificationType(Enum):
    """ 自动化通知方式 """
    # 默认通知: 不发送
    DEFAULT = 0
    # 钉钉通知
    DING_TALK = 1
    # 微信通知
    WECHAT = 2
    # 邮箱通知
    EMAIL = 3
    # 飞书通知
    FEI_SHU = 4