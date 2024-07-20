import json
import time
from fastapi import BackgroundTasks

from config.db import connect_to_mongo
from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scripts.popsy_scraper import (
    get_popsy_products_titles,
    get_popsy_products,
    get_popsy_product_variants,
)


# to scrape all products details from the database
def scrape_all_products(background_tasks: BackgroundTasks):
    
    db = connect_to_mongo()
    collection = db["popsy"]

    def scrape_variants(titles):
        start = time.perf_counter()

        for title in titles:
            logger.info(f"Scraping Variants for: {title}")
            products = get_popsy_products(title)
            if not products:
                continue
            for product in products:
                variants = get_popsy_product_variants(product["model"])
                if not variants["variants"]:
                    continue
                for variant in variants["variants"]:
                    popsy_variant = {
                        "product_id": variant["id"],
                        "model": variants["model"],
                        "variant_info": variant,
                        "brand": product["brand"],
                        "images": product["images"],
                        "metadata": product["metadata"],
                    }
                    if collection.find_one({"product_id": variant["id"]}):
                        collection.update_one(
                            {"product_id": variant["id"]}, {"$set": popsy_variant}
                        )
                        logger.info(f"Variant Updated: {title} - {variant['id']}")
                    else:
                        collection.insert_one(popsy_variant)
                        logger.info(f"Variant Added: {title} - {variant['id']}")
        end = time.perf_counter()
        
        print(f"⏱️ Popsy data scraping took {end - start:0.2f} seconds")
        logger.info(f"Popsy data scraping took {end - start:0.2f} seconds")

    all_titles = get_popsy_products_titles()
    background_tasks.add_task(scrape_variants, all_titles)

    return ResponseModel("Popsy products data updating in background.", [])
