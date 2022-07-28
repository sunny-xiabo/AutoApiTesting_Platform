"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : run.py
# @Date : 2022/7/19 3:58 下午
"""

import os
import traceback
import pytest

from Enums.notificationType_enum import NotificationType
from utils.logUtils.logControl import INFO
from utils.noticUtils.SendEmailControl import SendEmail
from utils.otherUtils.get_conf_data import project_name, get_excel_report_switch, get_notification_type
from utils.noticUtils.WeChatSendControl import WeChatSend
from utils.noticUtils.LarkControl import FeiShuTalkChatBot
from utils.noticUtils.dingTalkControl import DingTalkSendMsg
from utils.readFileUtils.caseAutoMaticControl import TestCaseAutomaticGeneration
from utils.otherUtils.allureData.error_case_excel import ErrorCaseExcel


def run():
    # 从配置文件中获取项目名称
    try:
        INFO.logger.info(
            """
    
             █████╗ ██╗   ██╗████████╗ ██████╗  █████╗ ██████╗ ██╗████████╗███████╗███████╗████████╗██╗███╗   ██╗ ██████╗ 
            ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝ 
            ███████║██║   ██║   ██║   ██║   ██║███████║██████╔╝██║   ██║   █████╗  ███████╗   ██║   ██║██╔██╗ ██║██║  ███╗
            ██╔══██║██║   ██║   ██║   ██║   ██║██╔══██║██╔═══╝ ██║   ██║   ██╔══╝  ╚════██║   ██║   ██║██║╚██╗██║██║   ██║
            ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║     ██║   ██║   ███████╗███████║   ██║   ██║██║ ╚████║╚██████╔╝
            ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    
            开始执行{}项目...
            """.format(project_name)
        )
        # 判断现有的测试用例，如果未生成测试代码，则自动生成
        TestCaseAutomaticGeneration().get_case_automatic()

        pytest.main(['-s', '-v','-W', 'ignore:Module already imported:pytest.PytestWarning',
                     '--alluredir', './reports/tmp', "--clean-alluredir"])
        """
                   --reruns: 失败重跑次数
                   --count: 重复执行次数
                   -v: 显示错误位置以及错误的详细信息
                   -s: 等价于 pytest --capture=no 可以捕获print函数的输出
                   -q: 简化输出信息
                   -m: 运行指定标签的测试用例
                   -x: 一旦错误，则停止运行
                   --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
                    "--reruns=3", "--reruns-delay=2"
        """
        os.system(r"allure generate ./reports/tmp -o ./reports/html --clean")
        # 判断通知类型，根据配置发送不同的报告通知
        if get_notification_type() == NotificationType.DEFAULT.value:
            pass
        elif get_notification_type() == NotificationType.DING_TALK.value:
            DingTalkSendMsg().send_ding_notification()
        elif get_notification_type() == NotificationType.WECHAT.value:
            WeChatSend().send_wechat_notification()
            if get_excel_report_switch():
                ErrorCaseExcel().write_case()
        elif get_notification_type() == NotificationType.EMAIL.value:
            SendEmail().send_main()
        elif get_notification_type() == NotificationType.FEI_SHU.value:
            FeiShuTalkChatBot().post()
        else:
            raise ValueError("通知类型配置错误，暂不支持该类型通知")
        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        # os.system(f"allure serve ./reports/tmp -h 127.0.0.1 -p 8800")

    except Exception:
        # 有异常发生，相关异常发送邮件
        error = traceback.format_exc()
        send_email = SendEmail()
        send_email.error_mail(error)
        raise


if __name__ == '__main__':
    run()
