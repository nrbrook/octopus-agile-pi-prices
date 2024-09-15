import logging
from abc import abstractmethod
from datetime import datetime, timezone
import pytz


class PriceInfo:
    def __init__(self, prices: list[dict]):
        self.prices = prices
        self.min_price = {'price': 999, 'valid_from': '1970-01-01 00:00:00'}
        self.min_price_index = 0
        total_price = 0

        for idx, price in enumerate(prices):
            if price['price'] < self.min_price['price']:
                self.min_price = price
                self.min_price_index = idx

            total_price += price['price']

        self.avg_price = total_price / len(prices)
        self.time_to_min_price = self.min_price_index / 2

        self.min_price_str = "{0:.1f}p".format(self.min_price['price'])
        self.min_price_duration_str = "{0:.1f}hrs".format(self.min_price_index/2)
        self.min_price_time = datetime.strptime(self.min_price['valid_from'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).astimezone(pytz.timezone('Europe/London')).strftime("%H:%M")


class DisplayAbstract:
    @abstractmethod
    def draw(self, prices: PriceInfo):
        raise NotImplementedError("Subclass must implement abstract method")

    def __init__(self, logger: logging.Logger, low_price: float):
        self.logger = logger
        self.low_price = low_price