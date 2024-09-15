import logging

from inky.auto import auto
#from font_hanken_grotesk import HankenGroteskBold, HankenGroteskMedium  # should you choose to switch to gross fonts
#from font_intuitive import Intuitive
from font_fredoka_one import FredokaOne  # this is the font we're currently using
from PIL import Image, ImageFont, ImageDraw

from display_abstract import DisplayAbstract, PriceInfo


class DisplayInky(DisplayAbstract):

    def colour_for_price(self, price):
        return self._inky_display.RED if price > self.low_price else self._inky_display.BLACK


    def draw_current_price(self, price, current_font_size, current_y_offset):
        font = ImageFont.truetype(FredokaOne, current_font_size)
        message = "{0:.1f}".format(price) + "p"
        w, h = font.getsize(message)
        #x = (inky_display.WIDTH / 2) - (w / 2)
        #y = (inky_display.HEIGHT / 2) - (h / 2)
        x = 0
        y = current_y_offset
        self._draw.text((x, y), message, self.colour_for_price(price), font)


    def draw_next_price(self, prices: PriceInfo, index, size, x_offset):
        if len(prices.prices) <= index + 1:
            return

        # NEXT
        message = "{0}:{1:.1f}p".format(index + 2, prices.prices[index+1]['price'])
        font = ImageFont.truetype(FredokaOne, size)
        w2, h2 = font.getsize(message)
        x = x_offset
        y = size * index
        colour = self.colour_for_price(prices.prices[index + 1]['price'])
        self._draw.text((x,y), message, colour, font)


    def draw_graph(self, prices: PriceInfo, bar_width, bar_height_per_p, bar_base_offset):
        if prices.min_price['price'] < 0:
            bar_base_offset += prices.min_price['price'] * bar_height_per_p

        for i, price in enumerate(prices.prices):
            scaled_price = price['price'] * bar_height_per_p
            ink_color = self.colour_for_price(price['price'])
            # takes a bit of thought this next bit, draw a rectangle from say x =  2i to 2(i-1) for each plot value
            # pixels_per_w defines the horizontal scaling factor (2 seems to work)
            self._draw.rectangle((bar_width*i,bar_base_offset,bar_width*(i-1),(bar_base_offset-scaled_price)),ink_color)


    def draw_lowest_price_text(self, right_column_offset, lowest_price_y_offset, lowest_price_font_size, index, msg):
        font = ImageFont.truetype(FredokaOne, lowest_price_font_size)
        self._draw.text((right_column_offset,lowest_price_y_offset + lowest_price_font_size * index), msg, self._inky_display.BLACK, font)


    def draw_all(self, prices: PriceInfo, current_font_size, current_y_offset, right_column_offset, right_column_text_size, bar_width, bar_height_per_p, bar_base_offset, lowest_price_font_size):
        # Current price
        self.draw_current_price(prices.prices[0]['price'], current_font_size, current_y_offset)


        # Next prices
        self.draw_next_price(prices, 0, right_column_text_size, right_column_offset)
        self.draw_next_price(prices, 1, right_column_text_size, right_column_offset)
        self.draw_next_price(prices, 2, right_column_text_size, right_column_offset)


        # Graph
        self.draw_graph(prices, bar_width, bar_height_per_p, bar_base_offset)


        # Lowest price
        # draw the bottom right min price and how many hours that is away
        lowest_price_y_offset = right_column_text_size * 3
        self.draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 0, "min:"+prices.min_price_str)
        self.draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 1, "in:"+prices.min_price_duration_str)
        self.draw_lowest_price_text(right_column_offset, lowest_price_y_offset, lowest_price_font_size, 2, "at:"+prices.min_price_time)


    def draw(self, prices: PriceInfo):
        if self._inky_display.WIDTH == 212: # low res display
            self.draw_all(
                prices,
                current_font_size=60,
                current_y_offset=-5,
                right_column_offset=145,
                right_column_text_size=20,
                bar_width=3,
                bar_height_per_p=2,
                bar_base_offset=104,
                lowest_price_font_size=15
            )
        else: # high res display
            self.draw_all(
                prices,
                current_font_size=72,
                current_y_offset=-10,
                right_column_offset=172,
                right_column_text_size=23,
                bar_width=3.5,
                bar_height_per_p=2.3,
                bar_base_offset=121,
                lowest_price_font_size=16
            )

        # render the actual image onto the display
        self._inky_display.set_image(self._img)
        self._inky_display.show()


    def __init__(self, logger: logging.Logger, low_price: float):
        super().__init__(logger, low_price)
        ##  -- Detect display type automatically
        try:
            self._inky_display = auto(ask_user=False, verbose=True)
        except TypeError:
            raise TypeError("You need to update the Inky library to >= v1.1.0")

        self._inky_display.set_border(self._inky_display.WHITE)
        self._img = Image.new("P", (self._inky_display.WIDTH, self._inky_display.HEIGHT))
        self._draw = ImageDraw.Draw(self._img)