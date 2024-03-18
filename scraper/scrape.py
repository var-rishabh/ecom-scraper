import json
from selectorlib import Extractor
import time
import threading

# utilities
from utils.url_utils import (
    raw_search_url,
    amazon_search_url,
    cartlow_search_url,
    noon_search_url,
)

from scraper.scripts.scrape_functions import scrape_product


# to scrape data for all products
def scrape_all(products):
    start = time.perf_counter()

    scraped_data = []
    threads = []

    for name in products:
        amazon_url, noon_url = raw_search_url(name["search_name"])

        # finding product search urls
        amazon_products_urls = amazon_search_url(amazon_url)
        noon_products_urls = noon_search_url(noon_url)
        cartlow_products_urls = cartlow_search_url(name["search_name"])

        info = {
            "product_id": name["product_id"],
            "brand": name["brand"],
            "name": name["name"],
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

    print(f"Finished in {round(stop - start, 2)} second(s)")

    return scraped_data
