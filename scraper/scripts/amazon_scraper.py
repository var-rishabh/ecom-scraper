import json
import random
import requests
from selectorlib import Extractor, Formatter

from config.logger import logger
from utils.file_utils import delete_file, save_data_to_html_file

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
    success_url_num = 0

    for url in amazon_products_urls:
        failed_tries = 0
        success_url_num += 1

        while failed_tries < MAX_TRIES:
            try:
                proxy = f"http://{random.choice(proxies_list)}"

                header = random.choice(headers.get("amazon", []))

                response = requests.get(
                    url, headers=header, proxies={"http": proxy}, timeout=20
                )
                if response.status_code == 200:
                    product_data = product_selector.extract(response.text)
                    if not product_data["seller"]:
                        product_data["seller"] = "Amazon.ae"
                    if product_data and product_data["name"]:
                        product_data["url"] = url
                        product_data["asin_number"] = url.split("/dp/")[1].split("/")[0]
                        delete_file(
                            product_name, "amazon", f"amazon{success_url_num}.html"
                        )
                        save_data_to_html_file(
                            product_name,
                            "amazon",
                            f"amazon{success_url_num}",
                            response.text,
                        )
                        products_data.append(product_data)
                        break
                else:
                    logger.warning(
                        f"🟠 Failed to fetch {product_name} from Amazon, {response.url}"
                    )
            except Exception as e:
                logger.error(
                    f"🟠 Error fetching data from {product_name} {url}", exc_info=True
                )

            failed_tries += 1
    return products_data
