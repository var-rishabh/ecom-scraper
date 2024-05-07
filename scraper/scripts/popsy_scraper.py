import json
import random
import requests

from config.logger import logger

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


# get all popsy products titles
def get_popsy_products_titles():
    try:
        url = "https://api.popsy.app/api/v2/product/titles?language=en"
        proxy = f"http://{random.choice(proxies_list)}"

        response = requests.get(url, proxies={"http": proxy})
        if response.status_code == 200:
            titles = response.text[1:-1].split(",")
            return titles
        else:
            return []

    except Exception as e:
        logger.error(f"Error in get_popsy_products_titles", exc_info=True)
        return []


# get all popsy products with title
def get_popsy_products(title):
    try:
        title = title.strip('"').replace(" ", "%20")
        url = (
            f"https://api.popsy.app/api/v2/product?country=AE&language=en&text={title}"
        )
        proxy = f"http://{random.choice(proxies_list)}"

        response = requests.get(url, proxies={"http": proxy}, timeout=20)
        if response.status_code == 200:
            products = response.json()
            return products["results"]
        else:
            return []

    except Exception as e:
        logger.error(f"Error in get_popsy_products", exc_info=True)
        return []


# get all popsy product variants
def get_popsy_product_variants(popsy_product_model):
    try:
        popsy_product_model = popsy_product_model.strip('"').replace(" ", "%20")
        url = f"https://api.popsy.app/api/v2/product/variants?country=AE&language=en&model={popsy_product_model}"

        proxy = f"http://{random.choice(proxies_list)}"

        response = requests.get(url, proxies={"http": proxy}, timeout=20)
        if response.status_code == 200:
            variants = response.json()
            return variants["model"][0]
        else:
            return []

    except Exception as e:
        logger.error(f"Error in get_popsy_product_variants", exc_info=True)
        return []
