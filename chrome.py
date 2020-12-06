from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


TIMEOUT_IN_SEC = 10.0


class ChromeDriver(object):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self._driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=chrome_options)
        self._driver.implicitly_wait(TIMEOUT_IN_SEC)

    def load(self, url: str) -> ChromeDriver:
        self._driver.get(url)
        return self

    def quit(self) -> None:
        self._driver.quit()

    def clickable_element(self, selector: str) -> ClickableElement:
        element = WebDriverWait(self._driver, TIMEOUT_IN_SEC).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        return ClickableElement(element)

    def wait(self, selector: str, count: int = 1, max_retries: int = 3) -> None:
        for _ in range(max_retries):
            found = WebDriverWait(self._driver, TIMEOUT_IN_SEC).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            if len(found) >= count:
                return
        raise ElementsNotFoundError(
            f'Could not find {count} instances of "{selector}"')

    def source(self) -> str:
        return self._driver.page_source


class ElementsNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ClickableElement(object):
    def __init__(self, web_element: WebElement):
        self._web_element = web_element

    def click_until_stale(self) -> None:
        while True:
            try:
                self._web_element.click()
            except StaleElementReferenceException:
                break
