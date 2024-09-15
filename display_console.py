from display_abstract import DisplayAbstract, PriceInfo


class DisplayConsole(DisplayAbstract):
    def draw(self, prices: PriceInfo):
        self.logger.info(f"Found {len(prices.prices)} prices in db")
        self.logger.info("Lowest price {0} in {1} at {2}".format(prices.min_price_str, prices.min_price_duration_str, prices.min_price_time))
        self.logger.info(f"Lowest price {prices.min_price_str} in {prices.min_price_duration_str} at {prices.min_price_time}")
        self.logger.info(f"Average price {prices.avg_price:.1f}p")
        self.logger.info(f"Time to lowest price {prices.time_to_min_price:.1f}hrs")