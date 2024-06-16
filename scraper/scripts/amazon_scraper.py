import time
import json
import random
import requests
from datetime import datetime
from selectorlib import Extractor, Formatter

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config.db import connect_to_mongo
from config.logger import logger

from utils.file_utils import delete_file, save_data_to_html_file

# getting all proxies list
proxies_list = open("config/proxies_list.txt", "r").read().strip().split("\n")
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


class PriceFormatter(Formatter):
    def format(self, text):
        if "AED" in text:
            return f"AED {text.split('AED')[1].strip()}"


class BookPriceFormatter(Formatter):
    def format(self, text):
        return text.replace("\xa0", " ").strip()


class RatingFormatter(Formatter):
    def format(self, text):
        if "out of 5" in text:
            return text.split(" out of 5")[0]


class ReviewCountFormatter(Formatter):
    def format(self, text):
        if "ratings" in text:
            return text.split(" ratings")[0]


formatters = Formatter.get_all()


# to get books data from google api
def google_books_api(isbn_number):
    failed_tries = 0
    book_data = {}
    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            response = requests.get(
                f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_number}",
                proxies={"http": proxy},
                timeout=20,
            )
            if response.status_code == 200:
                data = response.json()
                if data["totalItems"] > 0:
                    book_data["title"] = data["items"][0]["volumeInfo"].get("title", "")
                    book_data["subtitle"] = data["items"][0]["volumeInfo"].get(
                        "subtitle", ""
                    )
                    book_data["authors"] = data["items"][0]["volumeInfo"].get(
                        "authors", []
                    )
                    book_data["publisher"] = data["items"][0]["volumeInfo"].get(
                        "publisher", ""
                    )
                    book_data["published_date"] = data["items"][0]["volumeInfo"].get(
                        "publishedDate", ""
                    )
                    book_data["description"] = data["items"][0]["volumeInfo"].get(
                        "description", ""
                    )
                    book_data["categories"] = data["items"][0]["volumeInfo"].get(
                        "categories", []
                    )
                    book_data["language"] = data["items"][0]["volumeInfo"].get(
                        "language", ""
                    )
                    book_data["info_link"] = data["items"][0]["volumeInfo"].get(
                        "infoLink", ""
                    )
                    book_data["print_type"] = data["items"][0]["volumeInfo"].get(
                        "printType", ""
                    )
                    book_data["maturityRating"] = data["items"][0]["volumeInfo"].get(
                        "maturityRating", ""
                    )
                    book_data["isbn_10"] = (
                        data["items"][0]["volumeInfo"]
                        .get("industryIdentifiers", [])[0]
                        .get("identifier", "")
                    )
                    return book_data
                else:
                    logger.warning(
                        f"No book found {isbn_number} from Google Books API."
                    )
                    return book_data
            else:
                failed_tries += 1
                logger.warning(
                    f"Failed to fetch {isbn_number} from Google Books API. Trying again"
                )

        except Exception as e:
            failed_tries += 1
            logger.error(
                f"Error fetching data for {isbn_number} from Google Books API.",
                exc_info=True,
            )
    return book_data


# scraping multiple vendor prices
def scrape_multiple_vendors(product_url):
    logger.info(f"Scraping multiple vendors for {product_url}")

    from webdriver_manager.chrome import ChromeDriverManager

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        options=options, service=Service(ChromeDriverManager().install())
    )

    driver.get(product_url)

    parent_div = driver.find_element(By.CLASS_NAME, "daodi-content")
    anchor_tag = parent_div.find_element(By.CSS_SELECTOR, "a.a-link-normal")
    anchor_tag.click()

    time.sleep(3)

    vendor_list_container = driver.find_element(By.ID, "aod-offer-list")
    vendor_elements = vendor_list_container.find_elements(By.ID, "aod-offer")
    all_vendors = []
    for index, vendor in enumerate(vendor_elements):
        vendor_info = vendor.find_element(By.ID, "aod-offer-soldBy")
        vendor_name = vendor_info.find_element(By.CSS_SELECTOR, "a").text

        try:
            vendor_discount_price = vendor.find_element(
                By.XPATH,
                f'//*[@id="aod-price-{index + 1}"]/div[1]/span[2]/span[2]/span[2]',
            ).text
        except:
            vendor_discount_price = ""
        try:
            vendor_list_price = vendor.find_element(
                By.XPATH,
                f'//*[@id="aod-price-{index + 1}"]/div[2]/span/span[1]/span/span/span[2]',
            ).text
        except:
            try:
                vendor_whole_price = vendor.find_element(
                    By.XPATH,
                    f'//*[@id="aod-price-{index + 1}"]/div/span/span[2]/span[2]',
                ).text
                vendor_decimal_price = vendor.find_element(
                    By.XPATH,
                    f'//*[@id="aod-price-{index + 1}"]/div/span/span[2]/span[3]',
                ).text
                vendor_list_price = f"AED{vendor_whole_price}.{vendor_decimal_price}"
            except:
                vendor_list_price = ""

        all_vendors.append(
            {
                "vendor_name": vendor_name,
                "vendor_discount_price": vendor_discount_price,
                "vendor_list_price": vendor_list_price,
            }
        )

    driver.quit()

    logger.info(f"Scraped multiple vendors for {product_url}")

    return all_vendors


# scraping product details from amazon
def scrape_amazon(product_name, amazon_products_urls):
    if not amazon_products_urls:
        return

    product_selector = Extractor.from_yaml_file(
        "scraper/selectors/amazon/amazon_product.yml", formatters=formatters
    )
    products_data = []
    success_url_num = 0

    for url in amazon_products_urls:
        failed_tries = 0
        success_url_num += 1

        while failed_tries < MAX_TRIES:
            try:
                proxy = f"http://{random.choice(proxies_list)}"
                header = random.choice(headers.get("amazon", []))

                response = requests.get(
                    url, headers=header, proxies={"http": proxy}, timeout=20
                )
                if response.status_code == 200:
                    product_data = product_selector.extract(response.text)
                    if not product_data["seller"]:
                        product_data["seller"] = "Amazon.ae"
                    if product_data and product_data["name"]:
                        product_data["url"] = url
                        product_data["asin_number"] = url.split("/dp/")[1].split("/")[0]
                        if product_data["bullet_points"]:
                            new_bullet_points = product_data["bullet_points"]
                            product_data["bullet_points"] = []
                            for i in new_bullet_points:
                                product_data["bullet_points"].append(i["point"])
                        delete_file(
                            product_name, "amazon", f"amazon{success_url_num}.html"
                        )
                        save_data_to_html_file(
                            product_name,
                            "amazon",
                            f"amazon{success_url_num}",
                            response.text,
                        )
                        products_data.append(product_data)
                    break
                else:
                    failed_tries += 1
                    logger.warning(
                        f"🟠 Failed to fetch {product_name} from Amazon, {response.url}, {failed_tries}"
                    )
            except Exception as e:
                failed_tries += 1
                logger.error(
                    f"🟠 Error fetching data from {product_name} {url}, {failed_tries}",
                    exc_info=True,
                )

    return products_data


# scraping amazon products data from asin number
def scrape_amazon_asin(url):
    failed_tries = 0
    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            header = random.choice(headers.get("amazon", []))
            product_selector = Extractor.from_yaml_file(
                "scraper/selectors/amazon/amazon_product.yml", formatters=formatters
            )

            response = requests.get(
                url, headers=header, proxies={"http": proxy}, timeout=20
            )
            if response.status_code == 200:
                product_data = product_selector.extract(response.text)
                if product_data and product_data["name"]:
                    product_data["url"] = url
                    product_data["asin_number"] = url.split("/dp/")[1].split("/")[0]
                    if product_data["bullet_points"]:
                        new_bullet_points = product_data["bullet_points"]
                        product_data["bullet_points"] = []
                        for i in new_bullet_points:
                            product_data["bullet_points"].append(i["point"])
                    if not product_data["seller"]:
                        product_data["seller"] = "Amazon.ae"
                    product_data["updated_on"] = datetime.now()
                    if product_data["multiple_vendors"]:
                        product_data["multiple_vendors"] = scrape_multiple_vendors(url)

                    # saving data in mongodb
                    db = connect_to_mongo()
                    if db["amazon"].find_one(
                        {"asin_number": product_data["asin_number"]}
                    ):
                        db["amazon"].update_one(
                            {"asin_number": product_data["asin_number"]},
                            {"$set": product_data},
                        )
                        logger.info(
                            f"Updated data in Amazon, {product_data['asin_number']}"
                        )
                    else:
                        db["amazon"].insert_one(product_data)
                        logger.info(
                            f"Inserted data in Amazon, {product_data['asin_number']}"
                        )
                    break
                else:
                    logger.warning(
                        f"🟠 No data found on Amazon, Trying Again. {response.url}, {failed_tries}"
                    )
            else:
                failed_tries += 1
                logger.warning(
                    f"🟠 Failed to fetch from Amazon, {response.url}, {failed_tries}"
                )
        except Exception as e:
            failed_tries += 1
            logger.error(
                f"🟠 Error fetching data from {url}, {failed_tries}",
                exc_info=True,
            )


# to scrape amazon books details
def scrape_amazon_books_asin(url):
    failed_tries = 0
    while failed_tries < MAX_TRIES:
        try:
            proxy = f"http://{random.choice(proxies_list)}"
            header = random.choice(headers.get("amazon", []))
            product_selector = Extractor.from_yaml_file(
                "scraper/selectors/amazon/amazon_books.yml", formatters=formatters
            )

            book_data = google_books_api(url.split("/dp/")[1].split("/")[0])

            response = requests.get(
                url, headers=header, proxies={"http": proxy}, timeout=20
            )
            if response.status_code == 200:
                product_data = product_selector.extract(response.text)
                if product_data and product_data["name"]:
                    book_data["url"] = url
                    book_data["asin_number"] = url.split("/dp/")[1].split("/")[0]
                    book_data["hardcover_price"] = product_data["hardcover_price"]
                    book_data["paperback_price"] = product_data["paperback_price"]
                    book_data["images"] = product_data["images"]
                    if not "title" in book_data:
                        book_data["title"] = product_data["name"]
                    product_data["updated_on"] = datetime.now()
                    # saving data in mongodb
                    db = connect_to_mongo()
                    if db["books"].find_one({"asin_number": book_data["asin_number"]}):
                        db["books"].update_one(
                            {"asin_number": book_data["asin_number"]},
                            {"$set": book_data},
                        )
                        logger.info(
                            f"Updated data in Amazon, {book_data['asin_number']}"
                        )
                    else:
                        db["books"].insert_one(book_data)
                        logger.info(
                            f"Inserted data in Amazon, {book_data['asin_number']}"
                        )
                    break
                else:
                    logger.warning(
                        f"🟠 No data found on Amazon, {response.url}, {failed_tries}"
                    )
            else:
                failed_tries += 1
                logger.warning(
                    f"🟠 Failed to fetch from Amazon, {response.url}, {failed_tries}"
                )
        except Exception as e:
            failed_tries += 1
            logger.error(
                f"🟠 Error fetching book data from {url}, {failed_tries}",
                exc_info=True,
            )
