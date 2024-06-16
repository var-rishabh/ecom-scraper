import json
import random
import requests
import threading
from selectorlib import Extractor

from config.logger import logger
from config.db import connect_to_mongo
from utils.file_utils import delete_file, save_data_to_html_file
from utils.name_utils import clean_html_string

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10
CARTLOW_PARTNER_ID = "cartlow-buyback"
CARTLOW_PARTNER_SECRET = "rSnJ0HhVd46alb7Qa8zLtDfkDW2Ncduz8S7HaMk9ZAyb7FpJtduBgd8MINg2CGxGKi9dvPZmxdKw9PL3bcotwpiNc5JpW27s5AZyYDXkd57S6c5fb5rAcTw4"


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
                        product_data["discount_price"] = (
                            f"AED {product_data['discount_price']}"
                        )
                        product_data["list_price"] = f"AED {product_data['list_price']}"
                        if product_data["description"]:
                            new_description = product_data["description"]
                            product_data["description"] = " ".join(new_description)
                            product_data["description"] = clean_html_string(
                                product_data["description"]
                            )
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
                    f"🟣 Error fetching data from {product_name}, {failed_tries}",
                    exc_info=True,
                )
                failed_tries += 1

    return products_data


# scrape cartlow buyback categories
def get_cartlow_buyback_categories():
    failed_tries = 0
    cartlow_categories = []

    while failed_tries < MAX_TRIES:
        try:
            url = "https://tradein-api.cartlow.com/api/categories"
            header = random.choice(headers.get("cartlow", []))
            proxy = f"http://{random.choice(proxies_list)}"

            response = requests.post(
                url,
                json={
                    "partner_id": CARTLOW_PARTNER_ID,
                    "partner_secret": CARTLOW_PARTNER_SECRET,
                },
                headers=header,
                proxies={"http": proxy},
                timeout=20,
            )
            if response.status_code == 200 and response.json().get("status") == "true":
                data = response.json()
                for product in data["data"]:
                    cartlow_categories.append(
                        {
                            "category_id": product["category_id"],
                            "category_name": product["category_name"],
                            "category_image": product["category_image"],
                        }
                    )
                logger.info(
                    f"Got list of cartlow buyback categories. Total categories: {len(cartlow_categories)}"
                )
                break
            else:
                logger.warning(
                    f"Failed to get list of cartlow buyback categories. Retrying... (get_cartlow_buyback_categories) - {failed_tries}"
                )
                failed_tries += 1

        except Exception as e:
            logger.error(
                f"Error in getting cartlow buyback categories. Retrying... (get_cartlow_buyback_categories) - {failed_tries}",
                exc_info=True,
            )
            failed_tries += 1

    return cartlow_categories


# get all cartlow buyback brands
def get_cartlow_buyback_brands(all_categories):
    cartlow_brands = []

    def get_cartlow_brands_thread(category):
        failed_tries = 0
        while failed_tries < MAX_TRIES:
            try:
                url = "https://tradein-api.cartlow.com/api/category/brand"
                header = random.choice(headers.get("cartlow", []))
                proxy = f"http://{random.choice(proxies_list)}"

                response = requests.post(
                    url,
                    json={
                        "partner_id": CARTLOW_PARTNER_ID,
                        "partner_secret": CARTLOW_PARTNER_SECRET,
                        "category_id": category["category_id"],
                    },
                    headers=header,
                    proxies={"http": proxy},
                    timeout=20,
                )
                if (
                    response.status_code == 200
                    and response.json().get("status") == "true"
                ):
                    data = response.json()
                    for brand in data["data"]:
                        cartlow_brands.append(
                            {
                                "category_id": category["category_id"],
                                "category_name": category["category_name"],
                                "category_image": category["category_image"],
                                "brand_id": brand["brand_id"],
                                "brand_name": brand["brand_name"],
                                "brand_image": brand["image"],
                            }
                        )
                    logger.info(
                        f"Got list of cartlow buyback brands. Total brands: {len(cartlow_brands)}"
                    )
                    break
                else:
                    logger.warning(
                        f"Failed to get list of cartlow buyback brands. Retrying... (get_cartlow_brands_thread) - {failed_tries}"
                    )
                    failed_tries += 1

            except Exception as e:
                logger.error(
                    f"Error in getting cartlow buyback brands. Retrying... (get_cartlow_brands_thread) - {failed_tries}",
                    exc_info=True,
                )
                failed_tries += 1

    threads = []

    for category in all_categories:
        thread = threading.Thread(target=get_cartlow_brands_thread, args=(category,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return cartlow_brands


# get all cartlow buyback devices with price
def get_cartlow_buyback_devices_price(all_brands):
    db = connect_to_mongo()

    def get_cartlow_device_price_thread(brand):
        failed_tries = 0
        url = "https://tradein-api.cartlow.com/api/brand/devices"

        while failed_tries < MAX_TRIES:
            header = random.choice(headers.get("cartlow", []))
            proxy = f"http://{random.choice(proxies_list)}"
            try:
                response = requests.post(
                    url,
                    json={
                        "partner_id": CARTLOW_PARTNER_ID,
                        "partner_secret": CARTLOW_PARTNER_SECRET,
                        "category_id": brand["category_id"],
                        "brand_id": brand["brand_id"],
                    },
                    headers=header,
                    proxies={"http": proxy},
                    timeout=20,
                )
                if (
                    response.status_code == 200
                    and response.json().get("status") == "true"
                ):
                    res = response.json()
                    for product_id, product_data in res["data"].items():
                        product_info = {
                            "category_id": brand["category_id"],
                            "category_name": brand["category_name"],
                            "category_image": brand["category_image"],
                            "brand_id": brand["brand_id"],
                            "brand_name": brand["brand_name"],
                            "brand_image": brand["brand_image"],
                            "device_id": product_data["id"],
                            "device_name": product_data["device_name"],
                            "device_images": product_data["image"],
                            "prices": [],
                        }
                        for grade in product_data["grades"]:
                            price_info = {
                                "grade_title": grade["grade_title"],
                                "grade_conditions": grade["grade_condtions"],
                                "price": grade["pivot"]["grade_price"],
                            }
                            product_info["prices"].append(price_info)

                        # saving prices to db
                        if db["cartlow"].find_one(
                            {"device_id": product_info["device_id"]}
                        ):
                            db["cartlow"].update_one(
                                {"device_id": product_info["device_id"]},
                                {"$set": product_info},
                            )
                            logger.info(f"Updated cartlow buyback device price. {product_info['device_name']}")
                        else:
                            db["cartlow"].insert_one(product_info)
                            logger.info(f"Inserted cartlow buyback device price. {product_info['device_name']}")
                    break
                else:
                    logger.warning(
                        f"Failed to get cartlow buyback device price. Retrying... (get_cartlow_device_price_thread) - {failed_tries}"
                    )
                    failed_tries += 1

            except Exception as e:
                logger.error(
                    f"Error in getting cartlow buyback device price. Retrying... (get_cartlow_device_price_thread) - {failed_tries}",
                    exc_info=True,
                )
                failed_tries += 1

    threads = []

    for brand in all_brands:
        thread = threading.Thread(
            target=get_cartlow_device_price_thread, args=([brand])
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
