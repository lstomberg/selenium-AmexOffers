from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from collections import namedtuple
import logging
#
# Get around recaptcha with Selenium and Chrome
#
# 1. Hex edit out $cdc_ and $wdc_ from ChromeDriver
#    Use Hex Fiend on macOS
#    Open /usr/local/bin/ChromeDriver and rename $cdc_ and/or $wdc_ variables to something like $xcf_.
#      See https://www.blackhatworld.com/seo/how-to-bypass-slider-captcha-with-python-selenium.1041188/
# 2. add chrome options to disable infobar and exclude automation
#    options.add_argument("--disable-infobars")
#    options.add_experimental_option("excludeSwitches",["enable-automation"])
# 3. kill navigator.webdriver property from navigator.__proto__
#    wait for page to load using expected_conditions custom script consisting of
#      driver.execute_script("return document.readyState") == ("complete")
#    deleting property
#      driver.execute_script('delete navigator.__proto__.webdriver')
#

#
# STYLED PRINT
#


def slog(text):
    logging.debug("\033[2;37m{}\033[0m".format(text))


def log(text):
    logging.debug(text)

#
# Standard WebDriver
#


Selected = namedtuple('Selected', 'by value element')


class CaptchaEncountered(Exception):
    pass


class Base(webdriver.Chrome):

    class _NoneElement():
        def __getattr__(self, name):
            log("[NoneElement] '{}' called".format(name))

            def emptyMultiparameterFunc(a=0, b=0, c=0, d=0, e=0):
                for elem in [a, b, c, d, e]:
                    if elem != 0:
                        log(" input: {}".format(elem))
            return emptyMultiparameterFunc

    NoneElement = _NoneElement()
    USE_USER_PROFILE = False
    DEBUG = False

    #
    # Initialize
    #
    @classmethod
    def configureChromeOptions(self, chrome_options):
        # chrome_options.add_argument('window-size=801x842') #should be --window-size=x,y
        # chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        if self.USE_USER_PROFILE:
            chrome_options.add_argument(
                "user-data-dir=~/Library/Application Support/Google/Chrome/")

    def __init__(self, cwd_options=None, **kwargs):
        if cwd_options is None:
            cwd_options = Options()
        self.configureChromeOptions(cwd_options)
        super().__init__(**dict(kwargs, options=cwd_options))
        # self.set_window_position(0,0)

    @property
    def get_wait(self):
        # log("default was 60, changed to 20.  May want to change back?")
        return self._get_wait if getattr(self, '_get_wait', None) is not None else 20

    @get_wait.setter
    def get_wait(self, time):
        assert(type(time) is int)
        self._get_wait = time

    def get_url(self, url):
        log("[get_url] " + url)
        super().get(url)
        return self

    def get_one_of(self, xpaths, max_wait=20):
        index = 0
        for index in range(0, max_wait):
            offset = index % len(xpaths)
            xpath = xpaths[offset]
            # loop through each path every second, finishing on the first one found
            try:
                self._select(By.XPATH, xpath, wait=1)
            except Exception:
                continue
            return xpath

        # none found in max_wait time
        raise Exception()

    def get(self, xpath, wait=20, pause_on_except=True):
        return self._select(By.XPATH, xpath, wait, pause_on_except)

    def get_xpath(self, xpath):
        return self._select(By.XPATH, xpath)

    def get_id(self, elm_id):
        return self._select(By.ID, elm_id)

    def get_name(self, name):
        return self._select(By.NAME, name)

    def get_link(self, text):
        return self._select(By.LINK_TEXT, text)

    def get_link_partially(self, text):
        return self._select(By.PARTIAL_LINK_TEXT, text)

    def get_tag(self, tag):
        return self._select(By.TAG_NAME, tag)

    def get_class(self, class_name):
        return self._select(By.CLASS_NAME, class_name)

    def get_css(self, selector):
        return self._select(By.CSS_SELECTOR, selector)

    def gets(self, xpath, filter_invisible=False):
        slog("[gets] " + xpath)
        elmts = self._get_elmts(By.XPATH, xpath)
        if filter_invisible:
            elmts = [x for x in elmts if x.is_displayed()]
        return elmts

    def enable(self):
        # used to enable Terms check box on GCM
        self.execute_script(
            "arguments[0].removeAttribute('disabled','disabled')", self.selected.element)
        return self

    def enter(self, text):
        log("[enter] " + text)
        self.selected.element.send_keys(text)
        return self

    def submit(self):
        log("[submit]")
        sleep(1.0)
        self.selected.element.submit()
        return self

    def click(self):
        log("[click]")
        sleep(1.0)
        self.selected.element.click()
        return self

    def select(self, text):
        Select(self.selected.element).select_by_visible_text(text)
        return self

    def select_by_value(self, text):
        Select(self.selected.element).select_by_value(text)
        return self

    def scroll_into_view(self):
        # assumes last item gotten by xpath

        # xpath_script = "function getElementByXpath(path) { return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; }"
        # invocation = f"getElementByXpath(\'{self.selected.value}\').scrollIntoView(true);"
        # self.slog(xpath_script).slog(invocation)
        # self.execute_script(f"{xpath_script} {invocation}")

        # Issue: have to deal with " and ' in the xpath text I pass to function.  Try just this I guess??
        # at least in chrome ` is valid to encapsulate strings with " or ' or both
        # script = "document.evaluate(`{}`, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.scrollIntoView({})".format(
        #     self.selected.value, "{block: 'center'}")
        # self.execute_script(script)
        try:
            self.execute_script(
                "return arguments[0].scrollIntoView({block: 'center'});", self.selected.element)
        except Exception as ex:
            print(f"""Trying new form of scroll_into_view script execution but encountered exception :(
                -----------------------
                {ex}
                -----------------------
            """)
        return self

    def sleep(self, time):
        sleep(time)
        return self

    def clear(self):  # 2992658
        self.selected.element.clear()
        return self

    def print(self):
        print("[log] " + self.selected.element.text)
        return self

    #
    # LOGGING APIS
    #
    # Note: These log to info since I, the developer, am specifically calling it
    # Internal uses log() and slog(), not self.log() or self.slog()
    # s/log() logs to debug for now
    #
    def log(self, text):
        logging.info(text)
        return self

    def slog(self, text):
        logging.info(f"\033[2;37m{text}\033[0m")
        return self

    def element_text(self):
        if self.selected.element is self.NoneElement:
            return ""
        return self.selected.element.text

    def select_iframe(self, default=False):
        if default:
            self.switch_to.default_content()
        else:
            self.switch_to.frame(self.selected.element)
        return self

    def wait_until_invisible(self, xpath, time=45):
        log("[log] Waiting until invisible: {}".format(xpath))
        try:
            self._select(By.XPATH, xpath, 10)
            WebDriverWait(self, time).until(
                EC.invisibility_of_element_located((By.XPATH, xpath)))
        except:
            # either not found or time passed.  Should probably pause if time passed, not sure.
            pass
        return self

    # check for either captcha or element at xpath
    def get_or_captcha(self, xpath, captcha_xpath, except_on_captcha=False, except_on_captcha_timeout=True):
        # 60 seconds total
        for _ in range(0, 30):
            try:
                # look for transactions visible
                self._select(By.XPATH, xpath, wait=1, pause_on_except=False)
                # success
                return
            except TimeoutException:
                pass

            try:
                # look for Captcha visible
                self._select(By.XPATH, captcha_xpath,
                             wait=1, pause_on_except=False)
                # found
                break
            except TimeoutException:
                pass

        # captcha encountered or 60 seconds and nothing
        if except_on_captcha:
            raise CaptchaEncountered(
                "CaptchaEncountered(except_on_captcha=True)")

        # wait 60 seconds for Xpath to be found
        try:
            self._select(By.XPATH, xpath, wait=60, pause_on_except=False)
            # success
            return
        except TimeoutException:
            if except_on_captcha_timeout:
                raise CaptchaEncountered(
                    "CaptchaEncountered(except_on_captcha_timeout=True)")

        # captcha incomplete but shouldn't raise exception
        # self.selected is captcha
        return

    #
    # APIs
    #

    def _select(self, by, value, wait=20, pause_on_except=True):
        slog("[get] {} = {}".format(by, value))
        if self.DEBUG:
            log("press any key")  # , end='')
            input()
        condition = EC.visibility_of_element_located((by, value))
        field = Base.NoneElement
        field = WebDriverWait(
            self, min(wait, self.get_wait)).until(condition)

        self.selected = Selected(by, value, field)
        return self

    def _get_elmts(self, by, value):
        return self.find_elements(by, value)


class Headless(Base):

    @classmethod
    def configureChromeOptions(self, chrome_options):
        super().configureChromeOptions(chrome_options)
        chrome_options.add_argument('headless')
