import json
import random
import requests
from selectorlib import Extractor

from config.logger import logger
from utils.file_utils import delete_file, save_data_to_html_file

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


# scraping product details from cartlow
def scrape_cartlow(product_name, cartlow_products_urls):
    if not cartlow_products_urls:
        return

    product_selector = Extractor.from_yaml_file("scraper/selectors/cartlow_product.yml")

    products_data = []
    success_url_num = 0

    for url in cartlow_products_urls:
        failed_tries = 0
        success_url_num += 1

        while failed_tries < MAX_TRIES:
            try:
                proxy = f"http://{random.choice(proxies_list)}"
                header = random.choice(headers.get("cartlow", []))

                response = requests.get(
                    url, headers=header, proxies={"http": proxy}, timeout=10
                )
                if response.status_code == 200:
                    product_data = product_selector.extract(response.text)
                    if product_data and product_data["name"]:
                        product_data["url"] = url
                        product_data["discount_price"] = f"AED {product_data['discount_price']}"
                        product_data["list_price"] = f"AED {product_data['list_price']}"
                        if product_data["description"]:
                            new_description = product_data["description"]
                            product_data["description"] = " ".join(new_description)
                        delete_file(
                            product_name, "cartlow", f"cartlow{success_url_num}.html"
                        )
                        save_data_to_html_file(
                            product_name,
                            "cartlow",
                            f"cartlow{success_url_num}",
                            response.text,
                        )
                        products_data.append(product_data)
                        break
                else:
                    logger.warning(
                        f"🟣 Failed to fetch {product_name} from cartlow, {response.url}, {failed_tries}"
                    )
                    failed_tries += 1
            except Exception as e:
                logger.error(
                    f"🟣 Error fetching data from {product_name}, {failed_tries}", exc_info=True
                )
                failed_tries += 1


    return products_data
