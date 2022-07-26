"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : mysqlControl.py
# @Date : 2022/7/18 5:42 下午
"""

import datetime
import decimal
from warnings import filterwarnings

import pymysql

from common.setting import ConfigHandler
from utils.logUtils.logControl import ERROR
from utils.otherUtils.get_conf_data import sql_switch
from utils.readFileUtils.regularControl import sql_regular
from utils.readFileUtils.yamlControl import GetYamlData

# 忽略 MySQL 告警信息


filterwarnings("ignore", category=pymysql.Warning)


class MysqlDB(object):
    if sql_switch():

        def __init__(self):
            self.config = GetYamlData(ConfigHandler.config_path)
            self.read_mysql_config = self.config.get_yaml_data()['MySqlDB']

            try:
                # 建立数据库连接
                self.conn = pymysql.connect(
                    host=self.read_mysql_config['host'],
                    user=self.read_mysql_config['user'],
                    password=self.read_mysql_config['password'],
                    db=self.read_mysql_config['db']
                )

                # 使用 cursor 方法获取操作游标，得到一个可以执行sql语句，并且操作结果为字典返回的游标
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def __del__(self):
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def query(self, sql, state="all"):
            """
                查询
                :param sql:
                :param state:  all 是默认查询全部
                :return:
                """
            try:
                self.cur.execute(sql)

                if state == "all":
                    # 查询全部
                    data = self.cur.fetchall()

                else:
                    # 查询单条
                    data = self.cur.fetchone()

                return data
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def execute(self, sql: str):
            """
                更新 、 删除、 新增
                :param sql:
                :return:
                """
            try:
                # 使用 execute 操作 sql
                rows = self.cur.execute(sql)
                # 提交事务
                self.conn.commit()
                return rows
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))
                # 如果事务异常，则回滚数据
                self.conn.rollback()

        def assert_execution(self, sql: list, resp) -> dict:
            """
                执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会将所有数据以对象形式返回
                :param resp: 接口响应数据
                :param sql: sql
                :return:
                """
            try:
                if isinstance(sql, list):

                    data = {}
                    _sql_type = ['UPDATE', 'update', 'DELETE', 'delete', 'INSERT', 'insert']
                    if any(i in sql for i in _sql_type) is True:
                        raise ValueError("断言的 sql 必须是查询的 sql")
                    else:
                        for i in sql:
                            # 判断sql中是否有正则，如果有则通过jsonpath提取相关的数据
                            sql = sql_regular(i, resp)
                            # for 循环逐条处理断言 sql
                            query_data = self.query(sql)[0]
                            # 将sql 返回的所有内容全部放入对象中
                            for key, value in query_data.items():
                                if isinstance(value, decimal.Decimal):
                                    data[key] = float(value)
                                elif isinstance(value, datetime.datetime):
                                    data[key] = str(value)
                                else:
                                    data[key] = value

                        return data
                else:
                    raise ValueError("断言的查询sql需要是list类型")
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))
                raise

        def setup_sql_data(self, sql: list) -> dict:
            """
            处理前置请求sql
            :param sql:
            :return:
            """
            try:
                data = {}
                if isinstance(sql, list):
                    for i in sql:
                        sql_date = self.query(sql=i)[0]
                        for key, value in sql_date.items():
                            data[key] = value
                    return data
            except IndexError:
                raise ValueError("sql 数据查询失败，请检查setup_sql语句是否正确")


if __name__ == '__main__':
    pass
