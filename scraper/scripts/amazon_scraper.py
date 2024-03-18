import json
import random
import requests
from selectorlib import Extractor, Formatter

# saving the product details to a html file
from utils.file_utils import save_data_to_html_file

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


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

    product_selector = Extractor.from_yaml_file(
        "scraper/selectors/amazon_product.yml", formatters=formatters
    )

    products_data = []

    for url in amazon_products_urls:
        failed_tries = 0
        
        while failed_tries < MAX_TRIES:
            try:
                proxy = f"http://{random.choice(proxies_list)}"

                header = random.choice(headers.get("amazon", []))

                response = requests.get(url, headers=header, proxies={"http": proxy}, timeout=10)
                if response.status_code == 200:              
                    product_data = product_selector.extract(response.text)
                    if not product_data["seller"]:
                        product_data["seller"] = "Amazon.ae"
                    if product_data and product_data["name"]:
                        product_data["url"] = url
                        save_data_to_html_file(product_name, "amazon", response.text)
                        products_data.append(product_data)
                        break
                else:
                    print(f"🟠 Failed to fetch {product_name} from Amazon, {response.url}")
            except Exception as e:
                print(f"🟠 Error fetching data from {product_name}: {e}")
            failed_tries += 1

    return products_data
