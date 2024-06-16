import json
from selectorlib import Extractor
import time
import threading

from config.logger import logger

# utilities
from utils.url_utils import (
    raw_search_url,
    amazon_search_url,
    amazon_asin_url,
    cartlow_search_url,
    noon_search_url,
)

from scraper.scripts.scrape_functions import scrape_product
from scraper.scripts.amazon_scraper import scrape_amazon_asin, scrape_amazon_books_asin


# to scrape data for all products
def scrape_all(products):
    try:
        start = time.perf_counter()

        scraped_data = []
        threads = []

        for name in products:
            amazon_url, noon_url = raw_search_url(name["search_name"], name["model"])

            # finding product search urls
            amazon_products_urls = amazon_search_url(amazon_url)
            noon_products_urls = noon_search_url(noon_url)
            cartlow_products_urls = cartlow_search_url(name["search_name"])

            info = {
                "product_id": name["product_id"],
                "brand": name["brand"],
                "name": name["name"],
                "model": name["model"],
                "search_name": name["search_name"],
                "category": name["category"],
                "amazon": name["amazon"] if "amazon" in name else None,
                "cartlow": name["cartlow"] if "cartlow" in name else None,
                "noon": name["noon"] if "noon" in name else None,
            }

            thread = threading.Thread(
                target=scrape_product,
                args=(
                    name["search_name"],
                    amazon_products_urls,
                    cartlow_products_urls,
                    noon_products_urls,
                    info,
                ),
            )
            threads.append(thread)
            thread.start()

            scraped_data.append(info)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        stop = time.perf_counter()

        print(f"Finished scraping data in {round(stop - start, 2)} seconds.")
        logger.info(f"Finished scraping data in {round(stop - start, 2)} seconds.")

        return scraped_data

    except Exception as e:
        logger.error(f"Error scraping data.", exc_info=True)
        return []


# to scrape amazon data with asin number
def scrape_amazon_with_asin(asin_numbers):
    try:
        start = time.perf_counter()
        urls = []
        threads = []
        for asin_number in asin_numbers:
            thread = threading.Thread(
                target=amazon_asin_url,
                args=(asin_number, urls),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(len(urls))

        threads = []
        for url in urls:
            thread = threading.Thread(
                target=scrape_amazon_asin,
                args=({url}),
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        stop = time.perf_counter()

        print(f"Finished scraping data in {round(stop - start, 2)} seconds.")
        logger.info(f"Finished scraping data in {round(stop - start, 2)} seconds.")

    except Exception as e:
        logger.error(f"Error scraping data.", exc_info=True)


# to scrape amazon books data with asin number
def scrape_amazon_books(asin_numbers):
    try:
        start = time.perf_counter()
        urls = []
        threads = []
        for asin_number in asin_numbers:
            thread = threading.Thread(
                target=amazon_asin_url,
                args=(asin_number, urls),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(len(urls))

        threads = []
        for url in urls:
            thread = threading.Thread(
                target=scrape_amazon_books_asin,
                args=({url}),
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        stop = time.perf_counter()

        print(f"Finished scraping data in {round(stop - start, 2)} seconds.")
        logger.info(f"Finished scraping data in {round(stop - start, 2)} seconds.")

    except Exception as e:
        logger.error(f"Error scraping data.", exc_info=True)
