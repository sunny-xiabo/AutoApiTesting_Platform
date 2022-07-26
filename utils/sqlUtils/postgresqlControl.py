"""
# -*- coding:utf-8 -*-
# @Author: Summer
# @File : postgresqlControl.py
# @Date : 2022/7/20 3:01 下午
"""

import datetime
import decimal

import psycopg2
import psycopg2.extras
from warnings import filterwarnings
from utils.logUtils.logControl import ERROR
from common.setting import ConfigHandler
from utils.readFileUtils.regularControl import sql_regular
from utils.readFileUtils.yamlControl import GetYamlData
from utils.otherUtils.get_conf_data import sql_switch


# 忽略 postgreSQL 告警信息
# filterwarnings("ignore", category=psycopg2.Warning)


class PostgreDB(object):
    if sql_switch():
        def __init__(self):
            self.config = GetYamlData(ConfigHandler.config_path)
            self.read_postgresql_config = self.config.get_yaml_data()['PostgreDB']

            try:
                # 建议数据库连接
                self.conn = psycopg2.connect(
                    host=self.read_postgresql_config['host'],
                    user=self.read_postgresql_config['user'],
                    password=self.read_postgresql_config['password'],
                    port=self.read_postgresql_config['port'],
                    database=self.read_postgresql_config['database']
                )
                # 使用 cursor 方法获取操作游标,将结果转换成字典类型返回
                self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def __del__(self):  # 当执行完成后自动关闭对象  当创建多个对象时会触发del销毁上一个对象
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except Exception as e:
                ERROR.logger.error("数据库连接失败，失败原因{0}".format(e))

        def query(self, sql, state='all'):
            """
            查询
            @param sql:
            @param state: all 是默认查询全部
            @return:
            """
            try:
                # 执行sql
                self.cur.execute(sql)
                if state == 'all':
                    data = self.cur.fetchall()
                else:
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

        def setup_sql_data(self, sql):
            """
            处理前置请求sql
            @param sql:
            @return:
            """
            try:
                data = {}
                if isinstance(sql, list):
                    for i in sql:
                        sql_data = self.query(sql=i)[0]
                        for key, value in sql_data.items():
                            data[key] = value
                    return data

            except IndexError:
                raise ValueError("sql 数据查询失败，请检查setup_sql语句是否正确")


if __name__ == '__main__':
    p = PostgreDB()
    sql = "SELECT A.ID,b.project_id,b.floor_id FROM emission_source A INNER JOIN emission_source_project b ON A.ID=b.emission_source_id WHERE b.floor_id != -1;"
    print(p.query(sql))
