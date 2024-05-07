import threading
from datetime import datetime
from config.db import connect_to_mongo

# scrapers
from scraper.scripts.amazon_scraper import scrape_amazon
from scraper.scripts.cartlow_scraper import scrape_cartlow
from scraper.scripts.noon_scraper import scrape_noon


# Function to scrape data for a single product
def scrape_product(
    name, amazon_products_urls, cartlow_products_urls, noon_products_urls, scraped_data
):
    amazon_data = []
    noon_data = []
    cartlow_data = []

    threads = [
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_amazon,
                amazon_data,
                name,
                amazon_products_urls,
                scraped_data,
                "amazon",
            )
        ),
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_cartlow,
                cartlow_data,
                name,
                cartlow_products_urls,
                scraped_data,
                "cartlow",
            )
        ),
        threading.Thread(
            target=lambda: scrape_and_store(
                scrape_noon, noon_data, name, noon_products_urls, scraped_data, "noon"
            )
        ),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


# Helper function to scrape data and store it in scraped_data
def scrape_and_store(scraper_func, data_var, name, urls, scraped_data, key):
    db = connect_to_mongo()

    attempts = 3
    while attempts > 0:
        data = scraper_func(name, urls)
        if data:
            data_var = data
            scraped_data[key] = data_var
            if db["products"].find_one({"product_id": scraped_data["product_id"]}):
                db["products"].update_one(
                    {"product_id": scraped_data["product_id"]},
                    {
                        "$set": {
                            "amazon": scraped_data["amazon"],
                            "cartlow": scraped_data["cartlow"],
                            "noon": scraped_data["noon"],
                            "updated_on": f"{datetime.now()}",
                        }
                    },
                )
            else:
                db["products"].insert_one(
                    {
                        "product_id": scraped_data["product_id"],
                        "brand": scraped_data["brand"],
                        "name": scraped_data["name"],
                        "model": scraped_data["model"],
                        "category": scraped_data["category"],
                        "amazon": scraped_data["amazon"],
                        "cartlow": scraped_data["cartlow"],
                        "noon": scraped_data["noon"],
                        "updated_on": f"{datetime.now()}",
                    }
                )
            break
        else:
            attempts -= 1
            if attempts == 0:
                if db["products"].find_one({"product_id": scraped_data["product_id"]}):
                    db["products"].update_one(
                        {"product_id": scraped_data["product_id"]},
                        {
                            "$set": {
                                "amazon": (
                                    scraped_data["amazon"]
                                    if scraped_data["amazon"]
                                    else []
                                ),
                                "cartlow": (
                                    scraped_data["cartlow"]
                                    if scraped_data["cartlow"]
                                    else []
                                ),
                                "noon": (
                                    scraped_data["noon"] if scraped_data["noon"] else []
                                ),
                            }
                        },
                    )
