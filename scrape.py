import json
from selectorlib import Extractor
import time
import threading

# utilities
from utils.file_utils import read_product_names, save_data_to_js_file
from utils.url_utils import (
    raw_search_url,
    amazon_search_url,
    cartlow_search_url,
    noon_search_url,
)

# scrapers
from scrapers.amazon import scrape_amazon
from scrapers.cartlow import scrape_cartlow
from scrapers.noon import scrape_noon


# Function to scrape data for a single product
def scrape_product(
    name, amazon_products_urls, cartlow_products_urls, noon_products_urls, scraped_data
):
    amazon_data = None
    noon_data = None
    cartlow_data = None

    threads = [
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_amazon,
                amazon_data,
                name,
                amazon_products_urls,
                scraped_data,
                "Amazon",
            )
        ),
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_noon, noon_data, name, noon_products_urls, scraped_data, "Noon"
            )
        ),
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_cartlow,
                cartlow_data,
                name,
                cartlow_products_urls,
                scraped_data,
                "Cartlow",
            )
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


# Helper function to scrape data and store it in scraped_data
def scrape_and_store(scraper_func, data_var, name, urls, scraped_data, key):
    attempts = 3
    while attempts > 0:
        data = scraper_func(name, urls)
        if data:
            data_var = data
            scraped_data[name][key] = data_var
            break
        else:
            attempts -= 1
            if attempts == 0:
                scraped_data[name][key] = None


def main():
    start = time.perf_counter()

    product_names = read_product_names("data/product_names.txt")
    scraped_data = {}
    threads = []

    for name in product_names:
        amazon_url, noon_url = raw_search_url(name)

        # finding product search urls
        amazon_products_urls = amazon_search_url(amazon_url)
        noon_products_urls = noon_search_url(noon_url)
        cartlow_products_urls = cartlow_search_url(name)

        scraped_data[name] = {}

        thread = threading.Thread(
            target=scrape_product,
            args=(
                name,
                amazon_products_urls,
                cartlow_products_urls,
                noon_products_urls,
                scraped_data,
            ),
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    stop = time.perf_counter()

    print(f"Finished in {round(stop - start, 2)} second(s)")

    save_data_to_js_file(scraped_data)


if __name__ == "__main__":
    main()
