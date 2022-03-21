# (c) 2022 Warren Usui
# Collect pick data from an ESPN NCAA Tournament group
# This code is licensed under the MIT license (see LICENSE.txt for details)
"""
Handle the selenium setup and login to the ESPN website
"""
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller

def get_espn_driver_wrap():
    """
    Extract the username, password, and group name from the ini.file
    Use username/password combination to create a driver

    @return tuple selenium driver, and the name of the group
    """
    config = ConfigParser()
    config.read('march_madness.ini')
    parse_info = config["DEFAULT"]
    driver = get_espn_driver(parse_info["username"], parse_info["password"])
    group = ""
    if "group" in parse_info:
        group = parse_info["group"]
    number = ""
    if "number" in parse_info:
        number = str(parse_info["number"])
    return driver, group, number

def wait_get(wtime, driver, locator):
    """
    Wait while selenium displays stuff

    @param wtime integer seconds until timeout if object is not present
    @param driver object Selenium driver
    @param locator tuple Selenium webdriver locator we are waiting for

    @return object Webelement that we are waiting for
    """
    try:
        _ = WebDriverWait(driver, wtime).until(
            EC.presence_of_element_located(locator)
        )
    except TimeoutException:
        print("Aaargh!! Bad News!!")
    return driver.find_element(locator[0], locator[1])

def get_espn_driver(in_user, in_passwd):
    """
    Main infrastructure to log into the ESPN site

    @param in_user String ESPN user name
    @param in_passwd Password for in_user
    @return selenium driver logged into ESPN.  Webpage is displayed
    """
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get('https://www.espn.com/')
    search_box = wait_get(4, driver, (By.ID, "global-user-trigger"))
    search_box.click()
    nextbox = wait_get(4, driver, (By.XPATH, "//a[@data-affiliatename='espn']"))
    nextbox.click()
    driver.switch_to.frame("disneyid-iframe")
    username = wait_get(4, driver, (By.XPATH,
                    "//input[@placeholder='Username or Email Address']"))
    username.send_keys(in_user)
    password = wait_get(4, driver, (By.XPATH,
                    "//input[@placeholder='Password (case sensitive)']"))
    password.send_keys(in_passwd)
    button = wait_get(4, driver, (By.XPATH,
            "//button[@class='btn btn-primary btn-submit ng-isolate-scope']"))
    button.click()
    print("Waiting (Add security code if needed)")
    wait_get(180, driver, (By.ID, "main-container"))
    return driver
