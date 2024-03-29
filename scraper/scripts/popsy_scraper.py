import json
import random
import requests

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


# get all popsy products titles
def get_popsy_products_titles():
    url = "https://api.popsy.app/api/v2/product/titles?language=en"

    proxy = f"http://{random.choice(proxies_list)}"

    response = requests.get(url, proxies={"http": proxy})
    if response.status_code == 200:
        titles = response.text[1: -1].split(",")
        return titles
    else:
        return []


# get all popsy products with title
def get_popsy_products(title):
    title = title.strip('"').replace(" ", "%20")
    url = f"https://api.popsy.app/api/v2/product?country=AE&language=en&text={title}"

    proxy = f"http://{random.choice(proxies_list)}"

    response = requests.get(url, proxies={"http": proxy}, timeout=10)
    if response.status_code == 200:
        products = response.json()
        return products["results"]
    else:
        return []
    
    
# get all popsy product variants
def get_popsy_product_variants(popsy_product_model):
    popsy_product_model = popsy_product_model.strip('"').replace(" ", "%20")
    url = f"https://api.popsy.app/api/v2/product/variants?country=AE&language=en&model={popsy_product_model}"
    
    proxy = f"http://{random.choice(proxies_list)}"
    
    response = requests.get(url, proxies={"http": proxy}, timeout=10)
    if response.status_code == 200:
        variants = response.json()
        return variants["model"][0]
    else:
        return []