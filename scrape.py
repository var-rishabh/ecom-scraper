import json
from selectorlib import Extractor

# utilities
from utils.url_utils import generate_search_urls
from utils.file_utils import read_product_names, save_data_to_js_file

# scrapers
from scrapers.amazon import scrape_amazon


def main():
    product_names = read_product_names("data/product_names.txt")
    amazon_urls = generate_search_urls(product_names)

    amazon_products_urls = generate_amazon_search_urls(amazon_urls)

    data = {}

    # for product_name, amazon_url in zip(product_names, amazon_urls):
    #     amazon_data = scrape_amazon(amazon_url, amazon_extractor)
    #     if amazon_data:
    #         data[product_name] = {"amazon": amazon_data}

    # data["Amazon"] = scrape_amazon(product_names, amazon_urls, amazon_extractor)

    save_data_to_js_file(data)


if __name__ == "__main__":
    main()
