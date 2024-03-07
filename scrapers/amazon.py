import json
import requests
from selectorlib import Extractor, Formatter

# saving the product details to a html file
from utils.file_utils import save_data_to_html_file


class PriceFormatter(Formatter):
    def format(self, text):
        if "AED" in text:
            return f"AED {text.split('AED')[1].strip()}"


class RatingFormatter(Formatter):
    def format(self, text):
        if "out of 5" in text:
            return text.split(" out of 5")[0]


class ReviewCountFormatter(Formatter):
    def format(self, text):
        if "ratings" in text:
            return text.split(" ratings")[0]


formatters = Formatter.get_all()


# scraping product details from amazon
def scrape_amazon(product_name, amazon_products_urls):
    if not amazon_products_urls:
        return
    
    headers = json.loads(open("config/amazon_headers.json", "r").read())
    product_selector = Extractor.from_yaml_file(
        "selectors/amazon/productDetails.yml", formatters=formatters
    )

    products_data = []

    for url in amazon_products_urls:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"🟡 Failed to fetch {url}")
            continue

        product_data = product_selector.extract(response.text)
        if not product_data["seller"]:
            product_data["seller"] = "Amazon.ae"
        if product_data:
            product_data["url"] = url
            save_data_to_html_file(product_name, "Amazon", response.text)
            products_data.append(product_data)
        else:
            print(f"Failed to extract {url}")

    return products_data
