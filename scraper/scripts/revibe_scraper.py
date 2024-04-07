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
        if text and type(text) != type(None):
            return text.split("page=")[-1]
        return None


formatters = Formatter.get_all()


# get revibe category links
def get_revibe_category_links():
    failed_tries = 0
    category_links = []

    while failed_tries < MAX_TRIES:
        try:
            url = "https://revibe.me/"
            proxy = f"http://{random.choice(proxies_list)}"

            response = requests.get(url, proxies={"http": proxy}, timeout=20)
            if response.status_code == 200:
                url_selector = Extractor.from_yaml_file(
                    "scraper/selectors/revibe/revibe_category.yml",
                    formatters=formatters,
                )
                data = url_selector.extract(response.text)
                for item in data["category_urls"]:
                    if item["url"].startswith("/collections"):
                        category_links.append(
                            {
                                "name": item["name"],
                                "url": f"http://revibe.me{item['url']}",
                            }
                        )

                logger.info(f"Got revibe category links: {len(category_links)}")
                break
            else:
                logger.warning(
                    f"Failed to get revibe category links: {response.url}. Trying again."
                )
                failed_tries += 1
        except Exception as e:
            logger.error(f"Error scraping revibe category links.", exc_info=True)
            failed_tries += 1

    return category_links


# get revibe products links
def get_revibe_products_links(category_links):
    failed_tries = 0
    products_links = []

    page_number = 1

    for category_link in category_links:
        while failed_tries < MAX_TRIES:
            try:
                url = f'{category_link["url"]}?page={page_number}'

                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    url_selector = Extractor.from_yaml_file(
                        "scraper/selectors/revibe/revibe_url.yml",
                        formatters=formatters,
                    )
                    data = url_selector.extract(response.text)
                    if len(data["urls"]) > 0:
                        for item in data["urls"]:
                            products_links.append(
                                {
                                    "name": item["name"],
                                    "url": f"http://revibe.me{item['url']}",
                                }
                            )
                    page_number = data["nextPageNumber"]
                    if page_number == None:
                        break
                    logger.info(f"Got revibe products links: {len(products_links)}")
                else:
                    logger.warning(
                        f"Failed to get revibe products links: {response.url}. Trying again."
                    )
                    failed_tries += 1
            except Exception as e:
                logger.error(f"Error scraping revibe products links.", exc_info=True)
                failed_tries += 1

    return products_links


# def revibe variants
def scrape_revibe_variants(product_url):
    failed_tries = 0

    try:
        name = product_url["name"]
        url = product_url["url"]
        url_selector = Extractor.from_yaml_file(
            "scraper/selectors/revibe/revibe_product.yml",
            formatters=formatters,
        )

        while failed_tries < MAX_TRIES:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                data = url_selector.extract(response.text)
                product = None
                if len(data["product_info"]) > 0:
                    for item in data["product_info"]:
                        item = json.loads(item["info"])
                        if item["@type"] == "Product":
                            product = item
                if product:
                    db = connect_to_mongo()
                    for variant in product["offers"]:
                        split_name = variant["name"].rsplit(" - ", 1)
                        title = split_name[0]
                        properties = split_name[1].split(" / ")
                        if db["revibe"].find_one({"product_id": variant["sku"]}):
                            db["revibe"].update_one(
                                {"product_id": variant["sku"]},
                                {
                                    "$set": {
                                        "name": title,
                                        "price": variant["price"],
                                        "url": variant["url"],
                                        "image": variant["image"],
                                        "properties": properties,
                                        "description": variant["description"],
                                        "condition": variant["itemCondition"].rsplit(
                                            "/", 1
                                        )[1],
                                        "updated_at": datetime.now(),
                                    }
                                },
                            )
                            logger.info(f"Revent product updated: {variant['name']}")
                        else:
                            db["revibe"].insert_one(
                                {
                                    "product_id": variant["sku"],
                                    "name": title,
                                    "price": variant["price"],
                                    "url": variant["url"],
                                    "image": variant["image"],
                                    "properties": properties,
                                    "description": variant["description"],
                                    "condition": variant["itemCondition"].rsplit(
                                        "/", 1
                                    )[1],
                                    "updated_at": datetime.now(),
                                }
                            )
                            logger.info(f"Revent product added: {variant['name']}")
                break
            else:
                logger.warning(
                    f"Failed to get revibe product details: {response.url}. Trying again."
                )
                failed_tries += 1

    except Exception as e:
        logger.error(f"Error scraping revibe product details.", exc_info=True)
