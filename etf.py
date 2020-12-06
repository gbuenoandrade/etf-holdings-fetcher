from __future__ import annotations

import numpy as np
import datetime

from vanguard import VanguardETFFetcher
from html_parser import HTMLParser
from chrome import ChromeDriver
from vanguard import ETFFetcher
from price import YahooPriceProvider
from typing import List


class PositionFacade(object):
    def __init__(self, vanguard_fetcher: ETFFetcher, price_provider: YahooPriceProvider):
        self._vanguard_fetcher = vanguard_fetcher
        self._price_provider = price_provider

    def calculate_positions(self, ticker: str) -> (List[Position], datetime.datetime):
        holdings = self._vanguard_fetcher.holdings(ticker)
        tickers = [e.ticker for e in holdings.entries]
        prices = self._price_provider.get_prices(tickers)
        nav = self._vanguard_fetcher.nav(ticker)

        total_price = np.sum(
            (prices[e.ticker] * e.shares for e in holdings.entries))
        positions = []
        for e in holdings.entries:
            weight = nav * e.shares / total_price
            positions.append(Position(e.ticker, weight))
        return positions, holdings.date


class Position(object):
    def __init__(self, ticker: str, weight: float):
        self.ticker = ticker
        self.weight = weight

    def __repr__(self):
        return f'{self.ticker} - {self.weight}'
