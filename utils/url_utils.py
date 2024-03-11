import json
import random 
import requests
from selectorlib import Extractor, Formatter

proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 20


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
def raw_search_url(product_name):
    amazon_url = {
        "name": product_name,
        "link": f'https://www.amazon.ae/s?k={"+".join(product_name.split())}',
    }
    return amazon_url


# generating amazon product search url by matching product titles
def amazon_search_url(amazon_url):
    urls = []
    failed_tries = 0

    url_extractor = Extractor.from_yaml_file(
        "selectors/amazon/url.yml", formatters=formatters
    )

    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"

            header = random.choice(headers.get("amazon", []))

            response = requests.get(
                amazon_url["link"], headers=header, proxies={"http": proxy}, timeout=10
            )
            if response.status_code == 200:
                data = url_extractor.extract(response.text)
                for product in data["products"]:
                    product_name = product["brand"].lower() + product["title"].lower()
                    keywords = amazon_url["name"].lower().split()
                    matched = all(keyword in product_name for keyword in keywords)
                    if matched:
                        urls.append(product["url"])
                    if len(urls) == 5:
                        break
                failed_tries = 0
                return urls

            else:
                failed_tries += 1
                print(
                    f"🔸 Failed to fetch {amazon_url['link']}, {response.url}",
                    flush=True,
                )

        except Exception as e:
            failed_tries += 1
            print(f'🔸 Error fetching data from {amazon_url["link"]}: {e}')
