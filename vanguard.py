from __future__ import annotations

import datetime
from chrome import ChromeDriver
from html_parser import HTMLParser, Element
from typing import List

PCF_TEMPLATE = 'https://investor.vanguard.com/etf/profile/portfolio/%s/pcf'
OVERVIEW_TEMPLATE = 'https://investor.vanguard.com/etf/profile/overview/%s'


class VanguardFetcher(object):
    def __init__(self, driver: ChromeDriver, html_parser: HTMLParser, ticker: str):
        self._driver = driver
        self._html_parser = html_parser
        self.ticker = ticker

    def holdings(self) -> Holdings:
        url = PCF_TEMPLATE % self.ticker
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
    def _parse_holding_elements(holding_elements: List[Element]) -> List[Holding]:
        holdings = []
        for holding_element in holding_elements:
            elements = holding_element.find_all('td', {'class': 'ng-binding'})
            ticker = elements[0].content().replace('.', '-')
            sharesText = elements[2].content().replace(',', '')
            shares = int(sharesText)
            holdings.append(Holding(ticker, shares))
        return holdings

    def nav(self) -> float:
        url = OVERVIEW_TEMPLATE % self.ticker
        self._driver.load(url)
        selector = 'span[class="ng-scope ng-binding sceIsLayer arrange arrangeSec"'
        self._driver.wait(selector, count=5)

        self._parse_source()

        elements = self._html_parser.find_all(
            'span', {'class': 'ng-scope ng-binding sceIsLayer arrange arrangeSec'})
        nav = elements[4].content()[1:]
        return float(nav)

    def quit(self) -> None:
        self._driver.quit()


class Holdings(object):
    def __init__(self, date: datetime.datetime, holdings: List[Holding]):
        self.date = date
        self.holdings = holdings

    def __repr__(self):
        repr = f'As of {self.date}:\n'
        repr += '\n'.join(f'{idx+1} - {h}' for idx,
                          h in enumerate(self.holdings))
        return repr


class Holding(object):
    def __init__(self, ticker: str, shares: int):
        self.ticker = ticker
        self.shares = shares

    def __repr__(self):
        return f'(Ticker: {self.ticker}, Shares: {self.shares})'

