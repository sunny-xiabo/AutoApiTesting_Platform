## 框架介绍

本框架主要是基于 Python + pytest + allure + log + yaml + mysql + redis + 钉钉通知 + Jenkins 实现的接口自动化框架。


# 实现功能

* 测试数据隔离, 实现数据驱动
* 支持多接口数据依赖: 如A接口需要同时依赖B、C接口的响应数据作为参数
* 数据库断言: 直接在测试用例中写入查询的sql即可断言，无需编写代码
* 动态多断言: 如接口需要同时校验响应数据和sql校验，支持多场景断言
* 自动生成用例代码: 测试人员在yaml文件中填写好测试用例, 程序可以直接生成用例代码
* 代理录制: 支持代理录制，生成yaml格式的测试用例  
* 统计接口的运行时长: 拓展功能，订制开关，可以决定是否需要使用
* 日志模块: 打印每个接口的日志信息，同样订制了开关，可以决定是否需要打印日志
* 飞书、钉钉、企业微信通知: 支持多种通知场景，执行成功之后，可选择发送钉钉、飞书或者企业微信、邮箱通知
* 自定义拓展字段: 如用例中需要生成的随机数据，可直接调用
* 多线程执行

## 目录tree
    
        .
    ├── Cache                                 // 存放缓存文件
    ├── Enums                                 // 枚举文件
    │   ├── AllureAttachmentType_enum.py      // allure 报告的文件类型枚举
    │   ├── assertMethod_enum.py              // assert断言方法枚举
    │   ├── dependentType_enum.py             // 数据依赖相关枚举
    │   ├── notificationType_enum.py          // 通知方式枚举
    │   ├── requestType_enum.py               // request请求发送，请求参数的数据类型枚举
    │   └── yamlData_enum.py                  // yaml数据枚举
    ├── README.MD                             // 帮助文档
    ├── common                                // 配置目录
    │   ├── conf.yaml                         // 公共配置
    │   └── setting.py                        // 环境路径存放区域
    ├── data                                  // 测试用例数据存储区域
    │   ├── Login                             
    │   └── UserInfo
    ├── logs                                  // 日志存储区域
    │   ├── error.log
    │   ├── info.log
    │   └── warning.log
    ├── pytest.ini                            // pytest 基础配置
    ├── reports                               // 测试报告存储区域
    │   ├── html
    │   └── tmp
    ├── requirements.txt                      // 相关依赖库
    ├── run.py                                // 运行
    ├── test_cases                            // 测试用例代码
    │   ├── Login
    │   ├── UserInfo
    │   ├── __init__.py
    │   └── conftest.py                       // 
    ├── utils                                 // 工具类区域
    │   ├── __init__.py
    │   ├── assertUtils                       // 断言工具类
    │   ├── cacheUtils                        // 缓存工具类
    │   ├── logUtils                          // 日志工具类
    │   ├── mysqlUtils                        // 数据库工具类
    │   ├── noticUtils                        // 通知工具类
    │   ├── otherUtils                        // 其他工具类
    │   ├── readFileUtils                     // 文件操作工具类
    │   ├── recordingUtils                    // 代理录制工具类
    │   ├── requestsUtils                     // 请求工具类
    │   └── timesUtils                        // 时间工具类


## 安装
安装好依赖库后，需搭建python、jdk、allure 环境
如上环境如都搭建好，则安装本框架的所有第三方库依赖，执行如下命令

    pip3 install -r requirements.txt



## 如何创建用例

### 创建用例步骤
    1、在data文件夹下方创建相关的yaml用例
    2、写完之后，需要执行 utils\readFilesUtils\caseAutomaticControl.py 这个文件，生成自动化代码
    3、执行caseAutomaticControl.py文件之后，会发现，在test_case层新增该条用例的对应代码，可直接执行该用例调试
    4、当所有接口都编写好之后，可以直接运行run.py主程序，执行所有自动化接口




