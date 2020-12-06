from __future__ import annotations
from abc import ABC, abstractmethod

import datetime
from chrome import ChromeDriver
from html_parser import HTMLParser, Element
from typing import List

PCF_TEMPLATE = 'https://investor.vanguard.com/etf/profile/portfolio/%s/pcf'
OVERVIEW_TEMPLATE = 'https://investor.vanguard.com/etf/profile/overview/%s'


class ETFFetcher(ABC):
    @abstractmethod
    def holdings(self) -> Holdings:
        pass

    @abstractmethod
    def nav(self) -> float:
        pass

    @abstractmethod
    def quit(self) -> None:
        pass


class VanguardETFFetcher(ETFFetcher):
    def __init__(self, driver: ChromeDriver, html_parser: HTMLParser):
        self._driver = driver
        self._html_parser = html_parser

    def holdings(self, ticker: str) -> Holdings:
        url = PCF_TEMPLATE % ticker
        self._driver.load(url)
        self._expand_page()
        self._parse_source()

        raw_date = self._html_parser.find_first(
            'span', {'class': 'displayBlock ng-binding'}).content()
        date = datetime.datetime.strptime(raw_date, 'as of %m/%d/%Y')

        raw_elements = self._retrieve_holding_elements()
        holding_elements = self._parse_holding_elements(raw_elements)

        return Holdings(date, holding_elements)

    def _expand_page(self) -> None:
        selector = "a[data-ng-click='goToNextPage()'"
        next_page = self._driver.clickable_element(selector)
        next_page.click_until_stale()

    def _parse_source(self) -> None:
        html = self._driver.source()
        self._html_parser.parse(html)

    def _retrieve_holding_elements(self) -> List[Element]:
        elements = self._html_parser.find_all('tr', {
            'data-ng-repeat': 'curRow in dynamicData.pcfData.items ' +
            '| startFrom : pagination.startLoopFrom | limitTo : pagination.showUpto ' +
            '| orderBy : shareQuantity'}
        )
        elements = elements[:len(elements) // 2]
        return elements

    @staticmethod
    def _parse_holding_elements(holding_elements: List[Element]) -> List[Holdings.Entry]:
        holdings = []
        for holding_element in holding_elements:
            elements = holding_element.find_all('td', {'class': 'ng-binding'})
            ticker = elements[0].content().replace('.', '-')
            sharesText = elements[2].content().replace(',', '')
            shares = int(sharesText)
            holdings.append(Holdings.Entry(ticker, shares))
        return holdings

    def nav(self, ticker: str) -> float:
        url = OVERVIEW_TEMPLATE % ticker
        self._driver.load(url)
        selector = 'span[class="ng-scope ng-binding sceIsLayer arrange arrangeSec"'
        self._driver.wait(selector, count=5)
        self._parse_source()

        return self._parse_nav()

    def _parse_nav(self) -> float:
        elements = self._html_parser.find_all(
            'span', {'class': 'ng-scope ng-binding sceIsLayer arrange arrangeSec'})
        nav = elements[4].content()[1:]
        return float(nav)

    def quit(self) -> None:
        self._driver.quit()


class Holdings(object):
    class Entry(object):
        def __init__(self, ticker: str, shares: int):
            self.ticker = ticker
            self.shares = shares

        def __repr__(self):
            return f'(Ticker: {self.ticker}, Shares: {self.shares})'

    def __init__(self, date: datetime.datetime, entries: List[Entry]):
        self.date = date
        self.entries = entries

    def __repr__(self):
        repr = f'As of {self.date}:\n'
        repr += '\n'.join(f'{idx+1} - {h}' for idx,
                          h in enumerate(self.entries))
        return repr
