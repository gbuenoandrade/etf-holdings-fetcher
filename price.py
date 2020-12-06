import yfinance as yf
import time
from typing import List, TypedDict

MAX_RETRIES = 5


class YahooPriceProvider(object):
    # last close
    def get_prices(self, tickers: List[str]) -> TypedDict:
        data = YahooPriceProvider._download_prices_data(tickers)
        prices = [data['Close'][0]] if len(tickers) == 1 else [
            data[t]['Close'][0] for t in tickers]
        return {t: p for t, p in zip(tickers, prices)}

    @staticmethod
    def _download_prices_data(tickers: List[str], attempt: int = 1):
        if attempt > MAX_RETRIES:
            raise RuntimeError(f'Could not load prices for tickers {tickers}')
        try:
            return yf.download(' '.join(tickers), period='1d', group_by='ticker')
        except:
            time.sleep(1)
            return YahooPriceProvider._download_prices_data(tickers, attempt+1)
