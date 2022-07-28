# coding=utf-8
from selenium import webdriver
import os

# chrome_driver = os.path.abspath(r"/opt/webDriver/chromedriver")
# os.environ["webdriver.chrome.driver"] = chrome_driver
chrome_capabilities = {
    "browserName": "chrome",
    "version": "",
    "platform": "ANY",
    "javascriptEnabled": True,
    # "webdriver.chrome.driver": chrome_driver
}
browser = webdriver.Remote("http://http://124.223.178.186/:4444/wd/hub", desired_capabilities=chrome_capabilities)
browser.get("http://www.163.com")
print(browser.title)
browser.get_screenshot_as_file(r"/Users/xiabo/SoftwareTest/carbonPy/AutoApi_Platform/Files")
browser.quit()