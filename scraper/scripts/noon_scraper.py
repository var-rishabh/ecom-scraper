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


class TitleFormatter(Formatter):
    def format(self, text):
        if "UAE | Dubai, Abu Dhabi" in text:
            return text.split(" UAE | Dubai, Abu Dhabi")[0]
        else:
            return text


class PriceFormatter(Formatter):
    def format(self, text):
        if "Inclusive of VAT" in text:
            return text.split(" Inclusive of VAT")[0]
        else:
            return text


class ReviewFormatter(Formatter):
    def format(self, text):
        text = text.split(" ")
        if len(text) == 4:
            return text[2]
        else:
            return text


formatters = Formatter.get_all()


# scraping product details from noon
def scrape_noon(product_name, noon_products_urls):
    if not noon_products_urls:
        return

    product_selector = Extractor.from_yaml_file(
        "scraper/selectors/noon_product.yml", formatters=formatters
    )

    products_data = []
    success_url_num = 0

    for url in noon_products_urls:
        failed_tries = 0
        success_url_num += 1

        while failed_tries < MAX_TRIES:
            try:
                proxy = f"http://{random.choice(proxies_list)}"
                header = random.choice(headers.get("noon", []))

                response = requests.get(
                    url, headers=header, proxies={"http": proxy}, timeout=10
                )
                if response.status_code == 200:
                    product_data = product_selector.extract(response.text)
                    if product_data and product_data["name"]:
                        if product_data["grade"] and len(product_data["grade"]) == 2:
                            product_data["grade"] = product_data["grade"][1][
                                "renewed_grade"
                            ]
                        product_data["url"] = url
                        other_data = json.loads(product_data["all_data"])
                        if other_data["props"]["pageProps"]["catalog"]["product"]["long_description"]:
                            product_data["description"] = other_data["props"]["pageProps"]["catalog"]["product"]["long_description"]
                        if other_data["props"]["pageProps"]["catalog"]["product"]["feature_bullets"]:
                            product_data["bullet_points"] = other_data["props"]["pageProps"]["catalog"]["product"]["feature_bullets"]
                        product_data["images"] = []
                        if other_data["props"]["pageProps"]["catalog"]["product"]["image_keys"]:
                            for image in other_data["props"]["pageProps"]["catalog"]["product"]["image_keys"]:
                                product_data["images"].append(f"https://f.nooncdn.com/p/{image}.jpg")
                        del product_data["all_data"]
                        delete_file(product_name, "noon", f"noon{success_url_num}.html")
                        save_data_to_html_file(
                            product_name,
                            "noon",
                            f"noon{success_url_num}",
                            response.text,
                        )
                        products_data.append(product_data)
                        break
                else:
                    logger.warning(
                        f"🟡 Failed to fetch {product_name} from noon, {response.url}, {failed_tries}"
                    )
                    failed_tries += 1
            except Exception as e:
                logger.error(
                    f"🟡 Error fetching data from {product_name} {url}, {failed_tries}", exc_info=True
                )
                failed_tries += 1

    return products_data
