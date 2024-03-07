import json
import requests
from selectorlib import Extractor, Formatter


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
def generate_amazon_search_url(amazon_url):
    headers = json.loads(open("config/amazon_headers.json", "r").read())

    urls = []
    url_extractor = Extractor.from_yaml_file(
        "selectors/amazon/url.yml", formatters=formatters
    )

    response = requests.get(amazon_url["link"], headers=headers)
    if response.status_code != 200:
        print(f"🔴 Failed to fetch {amazon_url['link']}", flush=True)
        return

    data = url_extractor.extract(response.text)
    for product in data["products"]:
        product_name = product["brand"].lower() + product["title"].lower()
        keywords = amazon_url["name"].lower().split()
        matched = all(keyword in product_name for keyword in keywords)
        if matched:
            urls.append(product["url"])
        if len(urls) == 5:
            break

    return urls
