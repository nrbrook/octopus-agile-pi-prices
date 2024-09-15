# this is the script you run every half hour by cron, best done about 20-30 seconds after the half hour to ensure
# that the right datetime is read in.
# For example --->   */30 * * * * sleep 20; /usr/bin/python3 octoprice_main_inky.py > /home/pi/cron.log

# NOTE - USAGE
# This script *won't work* unless you have run (python3 store_prices.py) at least once in the last 'n' hours (n is variable, it updates 4pm every day)
# You also need to update store_prices.py to include your own DNO region.

from datetime import datetime, timezone

import agile_prices
import logging
from logging.handlers import RotatingFileHandler
import argparse

from display_abstract import PriceInfo

default_low_price = 14.8

log_file_max_size = 1 * 1024 * 1024  # 5 MB
log_file_backup_count = 0  # Number of backup files to keep

logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Setup logging for output and errors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logger = logging.getLogger('octopriceLogger')
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", help="The price database", default="agileprices.sqlite")
    parser.add_argument("-l", "--log", help="The log file. If provided, will not log to stdout", default=None)
    parser.add_argument("-e", "--error", help="The error log file", default=None)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    parser.add_argument("--display", help="Display type", default="inky", choices=["inky", "dothat", "console"])
    parser.add_argument("--low_price", help="Low price threshold", default=default_low_price, type=float)
    args = parser.parse_args()

    if args.log:
        logger.debug(f"Logging to {args.log}")
        file_handler = RotatingFileHandler(args.log, maxBytes=log_file_max_size, backupCount=log_file_backup_count)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logger_formatter)
        logger.addHandler(file_handler)
    else:
        logger.addHandler(console_handler)

    if args.error:
        logger.debug(f"Logging errors to {args.error}")
        error_handler = RotatingFileHandler(args.error, maxBytes=log_file_max_size, backupCount=log_file_backup_count)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logger_formatter)
        logger.addHandler(error_handler)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # array of up to 48 dicts, sorted by time
    prices = agile_prices.get_prices_from_db('agileprices.sqlite', 48)

    if len(prices) == 0:
        logger.warning('No prices found!')
        exit(1)

    price_info = PriceInfo(prices)

    # get display class
    if args.display == "inky":
        from display_inky import DisplayInky
        display = DisplayInky(logger, args.low_price)
    elif args.display == "dothat":
        from display_dothat import DisplayDothat
        display = DisplayDothat(logger, args.low_price)
    else:
        from display_console import DisplayConsole
        display = DisplayConsole(logger, args.low_price)

    display.draw(price_info)




