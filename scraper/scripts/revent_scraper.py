from datetime import datetime
import json
import random
import requests
from selectorlib import Extractor, Formatter

from config.db import connect_to_mongo
from config.logger import logger

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")

MAX_TRIES = 10


class NextPageNumberFormatter(Formatter):
    def format(self, text):
        if type(text) == str:
            return text.split("/")[-2]
        else:
            return None


formatters = Formatter.get_all()


# get all revent products urls
def get_revent_products_links():
    failed_tries = 0
    products_links = []

    page_number = 1

    while type(page_number) == int:
        while failed_tries < MAX_TRIES:
            try:
                url = f"https://uae.revent.store/shop/page/{page_number}/"
                proxy = f"http://{random.choice(proxies_list)}"

                url_selector = Extractor.from_yaml_file(
                    "scraper/selectors/revent/revent_url.yml", formatters=formatters
                )

                response = requests.get(url, proxies={"http": proxy}, timeout=20)
                if response.status_code == 200:
                    products_data = url_selector.extract(response.text)
                    if len(products_data["products"]) > 0:
                        for product in products_data["products"]:
                            products_links.append(product)
                        page_number = products_data["nextPageNumber"]
                    else:
                        page_number = products_data["nextPageNumber"]
                        break
                else:
                    logger.warning(
                        f"Failed to get products links from revent store: {response.url}. Trying again."
                    )
                    failed_tries += 1

            except Exception as e:
                logger.error(
                    f"Error in getting products links from revent.", exc_info=True
                )
                failed_tries += 1

    return products_links


# get revent product details along with variants
def scrape_revent_variants(product):
    failed_tries = 0

    try:
        name = product["name"]
        url = product["url"]

        url_selector = Extractor.from_yaml_file(
            "scraper/selectors/revent/revent_product.yml", formatters=formatters
        )
        while failed_tries < MAX_TRIES:
            proxy = f"http://{random.choice(proxies_list)}"

            response = requests.get(url, proxies={"http": proxy}, timeout=20)
            if response.status_code == 200:
                product = {}

                product_data = url_selector.extract(response.text)
                data = json.loads(product_data["product_info"])
                product_group = None
                for item in data["@graph"]:
                    if item.get("@type") == "ProductGroup":
                        product_group = item
                        break

                if product_group:
                    product["name"] = (
                        product_group["name"]
                        .replace("Buy Refurbished", "")
                        .replace("in UAE", "")
                        .strip()
                    )
                    product["brand"] = (
                        product_group["brand"]["name"]
                        if product_group.get("brand")
                        else "NA"
                    )
                    product["category"] = (
                        product_group["category"]
                        if product_group.get("category")
                        else "NA"
                    )
                    product["product_id"] = product_group["productGroupID"]
                    product["properties"] = []
                    if len(product_group["additionalProperty"]) > 0:
                        for properties in product_group["additionalProperty"]:
                            product["properties"].append(
                                {properties["name"]: properties["value"]}
                            )

                    product["variants"] = []
                    if len(product_group["hasVariant"]) > 0:
                        for variant in product_group["hasVariant"]:
                            product["variants"].append(
                                {
                                    "name": variant["name"],
                                    "price": variant["offers"]["price"],
                                    "image": (
                                        variant["image"]
                                        if variant.get("image")
                                        else "NA"
                                    ),
                                    "color": (
                                        variant["color"]
                                        if variant.get("color")
                                        else "NA"
                                    ),
                                    "storage": (
                                        variant["storage"]
                                        if variant.get("storage")
                                        else "NA"
                                    ),
                                    "condition": (
                                        variant["condition"]
                                        if variant.get("condition")
                                        else "NA"
                                    ),
                                    "url": variant["offers"]["url"],
                                }
                            )

                    # saving product details to database by checking it exist or not
                    db = connect_to_mongo()

                    if db["revent"].find_one({"product_id": product["product_id"]}):
                        db["revent"].update_one(
                            {"product_id": product["product_id"]},
                            {
                                "$set": {
                                    "name": product["name"],
                                    "brand": product["brand"],
                                    "category": product["category"],
                                    "properties": product["properties"],
                                    "variants": product["variants"],
                                    "updated_on": f"{datetime.now()}",
                                }
                            },
                        )
                    else:
                        db["revent"].insert_one(
                            {
                                "product_id": product["product_id"],
                                "name": product["name"],
                                "brand": product["brand"],
                                "category": product["category"],
                                "properties": product["properties"],
                                "variants": product["variants"],
                                "updated_on": f"{datetime.now()}",
                            }
                        )

                    logger.info(f"Product details saved to database: {name}")
                    break
                else:
                    logger.warning(
                        f"Failed to get product details from revent store: {response.url}. Trying again."
                    )
                    failed_tries += 1
            else:
                logger.warning(
                    f"Failed to get product details from revent store: {response.url}. Trying again."
                )
                failed_tries += 1

    except Exception as e:
        logger.error(f"Error scraping revent products.", exc_info=True)
