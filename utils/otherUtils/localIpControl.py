"""
 # -*- coding:utf-8 -*-
 # @Author：xiabo
 # @File : localIpControl.py
 # @Date ：2022/7/18 21:47
"""

import socket

def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
