import json
from selectorlib import Extractor

# utilities
from utils.file_utils import read_product_names, save_data_to_js_file
from utils.url_utils import raw_search_url, amazon_search_url, cartlow_search_url, noon_search_url

# scrapers
from scrapers.amazon import scrape_amazon
from scrapers.cartlow import scrape_cartlow
from scrapers.noon import scrape_noon


def main():
    product_names = read_product_names("data/product_names.txt")

    scraped_data = {}

    for name in product_names:
        amazon_url, noon_url = raw_search_url(name)

        # finding product search urls with links
        amazon_products_urls = amazon_search_url(amazon_url)
        noon_products_urls = noon_search_url(noon_url)

        # finding product search urls with product name
        cartlow_products_urls = cartlow_search_url(name)
        
        # scrape product info from sites
        amazon_data = scrape_amazon(name, amazon_products_urls)
        cartlow_data = scrape_cartlow(name, cartlow_products_urls)
        noon_data = scrape_noon(name, noon_products_urls)

        scraped_data[name] = {
            "Amazon": amazon_data,
            "Cartlow": cartlow_data,
            "Noon": noon_data
        }

    save_data_to_js_file(scraped_data)


if __name__ == "__main__":
    main()
