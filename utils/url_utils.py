import json
import random
import requests
from selectorlib import Extractor, Formatter

from config.logger import logger
from utils.name_utils import transform_noon_url_name

proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


class AmazonUrlFormatter(Formatter):
    def format(self, text):
        if "ref=" in text:
            url_parts = text.split("ref=")
            formatted_url = url_parts[0]
        else:
            formatted_url = text
        return f"https://www.amazon.ae{formatted_url}"


formatters = Formatter.get_all()


# generating search url for product
def raw_search_url(product_name, model):
    amazon_url = {
        "name": product_name,
        "model": model,
        "link": f'https://www.amazon.ae/s?k={"+".join(product_name.split())}',
    }
    noon_url = {
        "name": product_name,
        "model": model,
        "link": f"https://www.noon.com/_svc/catalog/api/v3/u/search/?limit=50&originalQuery={transform_noon_url_name(product_name)}&q={transform_noon_url_name(product_name)}&sort%5Bby%5D=popularity&searchDebug=false&sort%5Bdir%5D=desc",
    }
    return amazon_url, noon_url


# finding amazon product search url by matching product titles
def amazon_search_url(amazon_url):
    urls = []
    failed_tries = 0

    url_extractor = Extractor.from_yaml_file(
        "scraper/selectors/amazon/amazon_url.yml", formatters=formatters
    )

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"

            header = random.choice(headers.get("amazon", []))

            response = requests.get(
                amazon_url["link"], headers=header, proxies={"http": proxy}, timeout=20
            )
            if response.status_code == 200:
                data = url_extractor.extract(response.text)
                for product in data["products"]:
                    product_name = (
                        product["brand"].lower() + " " + product["title"].lower()
                    )
                    keywords = amazon_url["name"].lower().split()
                    matched = all(keyword in product_name for keyword in keywords)
                    if matched or (
                        amazon_url["model"] != ""
                        and (amazon_url["model"].lower() in product_name)
                    ):
                        urls.append(product["url"])
                    if len(urls) == 5:
                        break

                failed_tries = 0
                return urls

            failed_tries += 1
            logger.warning(f"Failed to fetch {amazon_url['link']}. Trying again")

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data from {amazon_url['link']}", exc_info=True
            )


# find amazon product url with asin number
def amazon_asin_url(asin_number, urls):
    failed_tries = 0

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            header = random.choice(headers.get("amazon", []))
            url_extractor = Extractor.from_yaml_file(
                "scraper/selectors/amazon/amazon_url.yml",
                formatters=formatters,
            )

            response = requests.get(
                f"https://www.amazon.ae/s?k={asin_number}",
                headers=header,
                proxies={"http": proxy},
                timeout=20,
            )
            if response.status_code == 200:
                data = url_extractor.extract(response.text)
                if (
                    data["products"]
                    and "/sspa/click?" not in data["products"][0]["url"]
                ):
                    for product in data["products"]:
                        if asin_number == product["url"].split("/dp/")[1].split("/")[0]:
                            urls.append(product["url"])
                    logger.info(f"Fetched {asin_number} - (amazon_asin_url)")
                    break
                else:
                    failed_tries += 1
                    logger.warning(
                        f"Failed to fetch {asin_number} {failed_tries} - (amazon_asin_url 2). Trying again"
                    )
            else:
                failed_tries += 1
                logger.warning(
                    f"Failed to fetch {asin_number} {failed_tries} - (amazon_asin_url 1). Trying again"
                )

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data from {asin_number} {failed_tries} - (amazon_asin_url)",
                exc_info=True,
            )


# find amazon book url with asin number
def amazon_book_asin_url(asin_number):
    failed_tries = 0
    url = None

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            header = random.choice(headers.get("amazon", []))
            url_extractor = Extractor.from_yaml_file(
                "scraper/selectors/amazon/amazon_url.yml",
                formatters=formatters,
            )

            response = requests.get(
                f"https://www.amazon.ae/s?k={asin_number}",
                headers=header,
                proxies={"http": proxy},
                timeout=20,
            )
            if response.status_code == 200:
                data = url_extractor.extract(response.text)
                if (
                    data["products"]
                    and "/sspa/click?" not in data["products"][0]["url"]
                ):
                    for product in data["products"]:
                        if asin_number == product["url"].split("/dp/")[1].split("/")[0]:
                            url = product["url"]
                    logger.info(f"Fetched {asin_number} - (amazon_asin_url)")
                    break
                else:
                    failed_tries += 1
                    logger.warning(
                        f"Failed to fetch {asin_number} {failed_tries} - (amazon_asin_url 2). Trying again"
                    )
            else:
                failed_tries += 1
                logger.warning(
                    f"Failed to fetch {asin_number} {failed_tries} - (amazon_asin_url 1). Trying again"
                )

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data from {asin_number} {failed_tries} - (amazon_asin_url)",
                exc_info=True,
            )

    return url


# finding cartlow product search urls with product name
def cartlow_search_url(product_name):
    urls = []
    failed_tries = 0

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            body_data = {
                "brand": "",
                "category": "",
                "brandId": [],
                "shopId": [],
                "storeId": "",
                "categoryId": [],
                "sectionId": '""',
                "elementId": "",
                "conditionId": [],
                "priceMin": 1,
                "priceMax": 50000,
                "sortBy": "popularity",
                "subCategoryId": [],
                "query": product_name,
                "offset": 0,
            }

            response = requests.post(
                "https://www.cartlow.com/uae/en/search",
                proxies={"http": proxy},
                json=body_data,
            )

            data = response.json()
            if response.status_code == 200 and (
                data["success"] == True and len(data["results"]) > 0
            ):
                for product in data["results"]:
                    product_Title = product["title"].lower()
                    keywords = product_name.lower().split()
                    matched = all(keyword in product_Title for keyword in keywords)
                    if matched:
                        urls.append("https://www.cartlow.com" + product["url"])
                    if len(urls) == 5:
                        break

                failed_tries = 0
                return urls

            logger.warning(f"Failed to fetch {product_name} from Cartlow. Trying again")
            failed_tries += 1

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data for {product_name} from Cartlow.", exc_info=True
            )


# finding noon product search urls with product list url
def noon_search_url(noon_url):
    urls = []
    failed_tries = 0

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            header = random.choice(headers.get("noon", []))
            response = requests.get(
                noon_url["link"], headers=header, proxies={"http": proxy}, timeout=20
            )

            data = response.json()
            if response.status_code == 200 and len(data["hits"]) > 0:
                for product in data["hits"]:
                    product_Title = (
                        product["brand"].lower() + " " + product["name"].lower()
                    )
                    keywords = noon_url["name"].lower().split()
                    matched = all(keyword in product_Title for keyword in keywords)
                    if matched or (
                        noon_url["model"] != ""
                        and (noon_url["model"].lower() in product_Title)
                    ):
                        urls.append(
                            "https://www.noon.com/"
                            + product["url"]
                            + "/"
                            + product["sku"]
                            + "/p/?o="
                            + product["offer_code"]
                        )
                    if len(urls) == 5:
                        break

                failed_tries = 0
                return urls

            logger.warning(
                f"Failed to fetch {noon_url['name']} from Noon. Trying again"
            )
            failed_tries += 1

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data for {noon_url['name']} from Noon.", exc_info=True
            )
