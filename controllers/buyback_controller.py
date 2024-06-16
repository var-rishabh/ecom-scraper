import time
import csv
from io import StringIO

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

from config.db import connect_to_mongo
from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scripts.buyback_scraper import (
    get_buyback_brands,
    get_buyback_product,
    get_buyback_assets,
)
from scraper.scripts.cartlow_scraper import (
    get_cartlow_buyback_categories,
    get_cartlow_buyback_brands,
    get_cartlow_buyback_devices_price,
)
from utils.file_utils import get_file_data


def scrape_buyback_product():
    start = time.perf_counter()

    # getting all active buyback products
    all_brands = get_buyback_brands()

    # getting all buyback product
    all_products = get_buyback_product(all_brands)

    # getting all assets of a product along with properties and prices
    all_assets = get_buyback_assets(all_products)

    stop = time.perf_counter()

    print(
        f"Finished scraping all buyback products in {round(stop - start, 2)} seconds."
    )
    logger.info(
        f"Finished scraping all buyback products in {round(stop - start, 2)} seconds."
    )


def scrape_cartlow_buyback():
    start = time.perf_counter()

    # get cartlow buyback categories
    all_categories = get_cartlow_buyback_categories()

    # get cartlow buyback brands
    all_brands = get_cartlow_buyback_brands(all_categories)

    # get cartlow buyback devices
    all_devices = get_cartlow_buyback_devices_price(all_brands)

    stop = time.perf_counter()
    print(
        f"Finished scraping all cartlow buyback products in {round(stop - start, 2)} seconds."
    )
    logger.info(
        f"Finished scraping all cartlow buyback products in {round(stop - start, 2)} seconds."
    )


# to scrape all products details from the web
def scrape_all_prices(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(scrape_buyback_product)
        return ResponseModel("Revibe products data updating in background.", [])

    except Exception as e:
        logger.error("Error in scraping buyback products.", exc_info=True)
        return ErrorResponseModel("Error in scraping buyback products.", [])


# to return all products prices from northladder
def northladder_prices():
    db = connect_to_mongo()

    try:
        # products = db["buyback"].find({"category_name": "Smartwatch"}).sort("brand", 1)
        products = db["buyback"].find({})

        filename = "northladder.csv"
        header = [
            "product_name",
            "brand_name",
            "category_name",
            "name",
            "series",  # series, subseries
            "model",
            "storage",  # storage, storage memory, storage space
            "ram",
            "price",
            "condition",
            "processor",
            "variant",
            "generation",
            "year",
            "features",
            "screen_size",
            "case_type",  # case type, case type\t
            "condition_description",
            "properties",
        ]

        key_to_column = {
            "name": "name",
            "asset name": "name",
            "series": "series",
            "subseries": "series",
            "model": "model",
            "storage": "storage",
            "storage memory": "storage",
            "storage space": "storage",
            "ram": "ram",
            "processor": "processor",
            "variant": "variant",
            "generation": "generation",
            "year": "year",
            "features": "features",
            "screen size": "screen_size",
            "case type": "case_type",
            "case type\t": "case_type",
        }

        all_products = []
        for product in products:
            for price in product["prices"][0]["northladder"]:
                data = {
                    "product_name": product["product_name"],
                    "brand_name": product["brand_name"],
                    "category_name": product["category_name"],
                    "price": price["price"],
                    "condition": price["condition"],
                    "condition_description": price["condition_description"],
                    "properties": product["properties"],
                    "name": "",
                    "series": "",
                    "model": "",
                    "storage": "",
                    "ram": "",
                    "processor": "",
                    "variant": "",
                    "generation": "",
                    "year": "",
                    "features": "",
                    "screen_size": "",
                    "case_type": "",
                }
                for prop in product["properties"]:
                    key = prop["key"].lower()
                    column = key_to_column.get(key, "")
                    if column:
                        data[column] = prop["value"]
                all_products.append(data)

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(header)
        for product in all_products:
            csv_writer.writerow(
                [
                    product["product_name"],
                    product["brand_name"],
                    product["category_name"],
                    product["name"],
                    product["series"],
                    product["model"],
                    product["storage"],
                    product["ram"],
                    product["price"],
                    product["condition"],
                    product["processor"],
                    product["variant"],
                    product["generation"],
                    product["year"],
                    product["features"],
                    product["screen_size"],
                    product["case_type"],
                    product["condition_description"],
                    product["properties"],
                ]
            )

        csv_data.seek(0)
        logger.info(
            "Northladder products data downloaded successfully. CSV Generated. (/buyback/northladder_prices)"
        )

        return StreamingResponse(
            iter([csv_data.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )

    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        return ErrorResponseModel(500, "An error occurred.", "Internal server error.")


# to scrape cartlow buyback prices
def scrape_cartlow_prices(background_tasks: BackgroundTasks):
    try:
        logger.info("Cartlow Buyback prices scraping started.")
        background_tasks.add_task(scrape_cartlow_buyback)
        return ResponseModel("Cartlow products data updating in background.", [])
    except Exception as e:
        logger.error("Error in scraping cartlow products.", exc_info=True)
        return ErrorResponseModel("Error in scraping cartlow products.", [])


# to download cartlow buyback prices
def download_cartlow_prices():
    db = connect_to_mongo()

    try:
        products = db["cartlow"].find({})

        filename = "cartlow.csv"
        header = [
            "device_id",
            "device_name",
            "brand_name",
            "category_name",
            "grade_title",
            "price",
            "grade_conditions",
        ]

        all_products = []
        for product in products:
            for price in product["prices"]:
                data = {
                    "device_id": product["device_id"],
                    "device_name": product["device_name"],
                    "brand_name": product["brand_name"],
                    "category_name": product["category_name"],
                    "grade_title": price["grade_title"],
                    "price": "AED " + str(price["price"]),
                    "grade_conditions": price["grade_conditions"],
                }
                all_products.append(data)

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(header)
        for product in all_products:
            csv_writer.writerow(
                [
                    product["device_id"],
                    product["device_name"],
                    product["brand_name"],
                    product["category_name"],
                    product["grade_title"],
                    product["price"],
                    product["grade_conditions"],
                ]
            )

        csv_data.seek(0)
        logger.info(
            "Cartlow buyback products data downloaded successfully. CSV Generated. (/buyback/download-cartlow-prices)"
        )

        return StreamingResponse(
            iter([csv_data.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )

    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        return ErrorResponseModel(500, "An error occurred.", "Internal server error.")
