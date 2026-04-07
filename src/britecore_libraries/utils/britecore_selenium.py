"""Selenium BriteCore Module"""

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from britecore_libraries import logger
from britecore_libraries.config import settings
from britecore_libraries.exceptions import BritecoreError

retry = settings.web.retry
if not retry:
    retry = 5

wait_short = settings.web_timeout
if not wait_short:
    wait_short = 5

wait_long = settings.web.timeout_long
if not wait_long:
    wait_long = wait_short * 10

web_browser = settings.web_browser
if not web_browser:
    web_browser = "Edge"

if web_browser.lower() not in ("edge", "firefox", "chrome", "opera", "safari"):
    logger.error(f"Invalid browser specified - {web_browser}")

ignored_exceptions = (
    selenium.common.exceptions.ElementClickInterceptedException,
    selenium.common.exceptions.MoveTargetOutOfBoundsException,
    selenium.common.exceptions.TimeoutException,
    selenium.common.exceptions.ElementNotInteractableException,
)


def get_driver(
    browser: str = web_browser,
) -> (
    selenium.webdriver.Edge
    | selenium.webdriver.Firefox
    | selenium.webdriver.Chrome
    | selenium.webdriver.Safari
):
    """
    Gets Selenium driver
    :param browser: Type of browser to load
    :type browser: str
    :return: Selenium driver
    :rtype: Union[None, selenium.webdriver.edge.webdriver.WebDriver,
    selenium.webdriver.firefox.webdriver.WebDriver]
    """
    logger.info(f"Launching {browser}")
    driver_info = getattr(webdriver, browser)
    try:
        driver = driver_info()
    except Exception as err:  # skipcq PYL-W0703
        logger.error(f"Cannot launch browser - {err}")
        raise BritecoreError.Base(f"Cannot launch browser - {err}") from err

    driver.maximize_window()

    return driver


def bc_login(
    driver: (
        selenium.webdriver.Edge
        | selenium.webdriver.Firefox
        | selenium.webdriver.Chrome
        | selenium.webdriver.Safari
    ),
    url: str = settings.base_url,
    user: str = settings.web_user,
    password: str = settings.web_pass,
    role_select: bool = False,
) -> None:
    """
    Logs into BriteCore webpage
    :param driver: Selenium driver to use
    :type driver: selenium.webdriver.edge.webdriver.WebDriver
    :param url:BriteCore URL
    :type url: str
    :param user: Username
    :type user: str
    :param password: Password
    :type password: str
    :param role_select: If role selection is needed
    :type role_select: bool
    :return:
    :rtype: None
    """
    driver.get(url)

    login_box = driver.find_elements(By.CLASS_NAME, "el-input__inner")

    logger.debug(f"Logging into BriteCore as {settings.web_user}")
    user_box = login_box[0]
    pass_box = login_box[1]
    user_box.send_keys(user)
    pass_box.send_keys(password + Keys.ENTER)

    if role_select:
        user_role = WebDriverWait(driver, wait_long).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "form-control"))
        )
        user_role.send_keys("a")

        role_ok = driver.find_element(By.CLASS_NAME, "btn-primary")
        role_ok.click()

    web_title = ""
    while web_title != "Dashboard":
        web_title = driver.title


def __getattr__(name):
    return getattr("selenium", name)
