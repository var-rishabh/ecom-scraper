import time
import threading
from fastapi import BackgroundTasks

from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scripts.buyback_scraper import (
    get_buyback_brands,
    get_buyback_product,
    get_buyback_assets
)


def scrape_buyback_product():
    start = time.perf_counter()

    # getting all active buyback products
    all_brands = get_buyback_brands()

    # getting all buyback product 
    all_products = get_buyback_product(all_brands)

    # getting all assets of a product along with properties and prices
    all_assets = get_buyback_assets(all_products)

    stop = time.perf_counter()
    
    print(f"Finished scraping all buyback products in {round(stop - start, 2)} seconds.")
    logger.info(f"Finished scraping all buyback products in {round(stop - start, 2)} seconds.")


# to scrape all products details from the web
def scrape_all_prices(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(scrape_buyback_product)
        return ResponseModel("Revibe products data updating in background.", [])

    except Exception as e:
        logger.error("Error in scraping buyback products.", exc_info=True)
        return ErrorResponseModel("Error in scraping buyback products.", [])
