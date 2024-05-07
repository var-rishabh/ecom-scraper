import threading
import time
from fastapi import BackgroundTasks

from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scripts.revent_scraper import (
    get_revent_products_links,
    scrape_revent_variants,
)


def scrape_revent_product(product_links, total_time):
    start = time.perf_counter()

    threads = []

    for product in product_links:
        thread = threading.Thread(
            target=scrape_revent_variants,
            args=(product,),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    stop = time.perf_counter()

    print(f"Finished scraping all revent products in {round(stop - start + total_time, 2)} seconds.")
    logger.info(
        f"Finished scraping all revent products in {round(stop - start + total_time, 2)} seconds."
    )


# to scrape all products details from the web
def scrape_all_products(background_tasks: BackgroundTasks):
    try:
        # getting all products url from revent web
        start = time.perf_counter()
        all_products_links = get_revent_products_links()
        stop = time.perf_counter()
        
        background_tasks.add_task(scrape_revent_product, all_products_links, round(stop - start, 2))

        return ResponseModel("Revent products data updating in background.", [])

    except Exception as e:
        logger.error("Error in scraping revent products.", exc_info=True)
        return ErrorResponseModel("Error in scraping revent products.", [])
