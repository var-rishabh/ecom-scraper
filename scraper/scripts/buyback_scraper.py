import json
import time
import random
import requests
import threading
from datetime import datetime

from config.db import connect_to_mongo
from config.logger import logger

# getting all headers list
headers = json.loads(open("config/headers.json", "r").read())

MAX_TRIES = 10


# get all active buyback brands
def get_buyback_brands():
    failed_tries = 0

    get_buyback_brands = []

    while failed_tries < MAX_TRIES:
        try:
            url = "https://b2b-apiv7.northladder.com/b2b/category/active-list"
            header = random.choice(headers.get("northladder", []))

            response = requests.get(url, headers=header, timeout=20)
            if response.status_code == 200 and response.json().get("status") == True:
                data = response.json()
                for product in data["data"]:
                    for model in product["brands"]:
                        get_buyback_brands.append(
                            {
                                "category_id": product["_id"],
                                "category_name": product["categoryName"],
                                "category_type": product["type"],
                                "brand_id": model["_id"],
                                "brand_name": model["name"],
                            }
                        )
                logger.info(
                    f"Got active list of buyback brands. Total brands: {len(get_buyback_brands)}"
                )
                break
            else:
                logger.warning(
                    f"Failed to get active list of buyback brands. Retrying... (get_buyback_brands) - {failed_tries}"
                )
                failed_tries += 1

        except Exception as e:
            logger.error(
                f"Error in getting active buyback brands. Retrying... (get_buyback_brands) - {failed_tries}",
                exc_info=True,
            )
            failed_tries += 1

    return get_buyback_brands


# get all buyback product models
def get_buyback_product(buyback_brands):
    all_products = []

    def get_buyback_product_thread(brand):
        failed_tries = 0
        while failed_tries < MAX_TRIES:
            try:
                url = f'https://b2b-apiv7.northladder.com/b2b/asset/active-groups/{brand["category_id"]}/{brand["brand_id"]}'
                header = random.choice(headers.get("northladder", []))

                response = requests.get(url, headers=header, timeout=20)
                if (
                    response.status_code == 200
                    and response.json().get("status") == True
                ):
                    data = response.json()
                    for product in data["data"]:
                        all_products.append(
                            {
                                "category_id": brand["category_id"],
                                "category_name": brand["category_name"],
                                "category_type": brand["category_type"],
                                "brand_id": brand["brand_id"],
                                "brand_name": brand["brand_name"],
                                "product_id": product["_id"],
                                "product_name": product["name"],
                            }
                        )
                    logger.info(
                        f"Got active list of buyback products. Total products: {len(all_products)}"
                    )
                    break
                else:
                    logger.warning(
                        f"Failed to get active list of buyback products. Retrying... (get_buyback_product_thread) - {failed_tries}"
                    )
                    failed_tries += 1

            except Exception as e:
                logger.error(
                    f"Error in getting active buyback products. Retrying... (get_buyback_product_thread) - {failed_tries}",
                    exc_info=True,
                )
                failed_tries += 1

    threads = []

    for brand in buyback_brands:
        thread = threading.Thread(target=get_buyback_product_thread, args=(brand,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return all_products


# to get all assets of a product
def get_buyback_assets(all_products):
    header = random.choice(headers.get("northladder", []))

    def get_buyback_attribute_thread(url, product, attributes):
        try:
            response = requests.post(
                url, json={"attributes": attributes}, headers=header, timeout=20
            )
            if response.status_code == 200 and response.json().get("status") == True:
                data = response.json()["data"]
                if not data["isAttribAvailable"]:
                    asset_details = {
                        "asset_id": data["assetInfo"]["_id"],
                        "brand_id": product["brand_id"],
                        "brand_name": product["brand_name"],
                        "product_name": product["product_name"],
                        "category_id": product["category_id"],
                        "category_name": product["category_name"],
                        "category_type": product["category_type"],
                        "product_id": product["product_id"],
                        "product_name": product["product_name"],
                        "properties": [],
                    }
                    for attribute in data["assetInfo"]["attributes"]:
                        asset_details["properties"].append(
                            {"key": attribute["key"], "value": attribute["value"]}
                        )
                    get_buyback_prices(asset_details)
                    logger.info(f"Got active list of buyback assets.")
                    return
                else:
                    threads = []
                    for attribute_value in data["attributes"]["values"]:
                        thread = threading.Thread(
                            target=get_buyback_attribute_thread,
                            args=(
                                url,
                                product,
                                attributes
                                + [
                                    {
                                        "key": data["attributes"]["key"],
                                        "value": attribute_value,
                                    }
                                ],
                            ),
                        )
                        thread.start()
                        threads.append(thread)
                    for thread in threads:
                        thread.join()
            else:
                logger.warning(
                    f"Failed to get active list of buyback assets. Retrying... (get_buyback_attribute_thread)"
                )
        except Exception as e:
            logger.error(
                f"Error in getting active buyback assets. Retrying... (get_buyback_attribute_thread)",
                exc_info=True,
            )

    def get_buyback_assets_thread(product):
        failed_tries = 0
        url = f'https://b2b-apiv7.northladder.com/b2b/asset/active-asset-attributes/{product["product_id"]}'

        while failed_tries < MAX_TRIES:
            try:
                response = requests.post(
                    url, json={"attributes": []}, headers=header, timeout=40
                )
                if (
                    response.status_code == 200
                    and response.json().get("status") == True
                ):
                    data = response.json()["data"]
                    if data["isAttribAvailable"]:
                        for attribute_value in data["attributes"]["values"]:
                            get_buyback_attribute_thread(
                                url,
                                product,
                                [
                                    {
                                        "key": data["attributes"]["key"],
                                        "value": attribute_value,
                                    }
                                ],
                            )
                    break
                else:
                    logger.warning(
                        f"Failed to get active list of buyback assets. Retrying... (get_buyback_assets_thread) - {failed_tries}"
                    )
                    failed_tries += 1

            except Exception as e:
                logger.error(
                    f"Error in getting active buyback assets. Retrying... (get_buyback_assets_thread) - {failed_tries}",
                    exc_info=True,
                )
                failed_tries += 1

    threads = []

    for product in all_products:
        thread = threading.Thread(target=get_buyback_assets_thread, args=([product]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


# to get all prices of an asset with condition
def get_buyback_prices(asset):
    def get_buyback_individual_thread(asset, info, prices):
        web_name = info
        failed_tries = 0

        header = None
        if info == "northladder":
            header = random.choice(headers.get("northladder", []))
        elif info == "revibe":
            header = random.choice(headers.get("revibe", []))
        elif info == "revent":
            header = random.choice(headers.get("revent", []))

        while failed_tries < MAX_TRIES:
            url = (
                "https://b2b-apiv7.northladder.com/b2b/appraisal/free-quote/consolidate"
            )
            response = requests.post(
                url,
                json={
                    "assetId": asset["asset_id"],
                    "assetName": asset["product_name"],
                    "brandId": asset["brand_id"],
                    "brandName": asset["brand_name"],
                    "buyBackTimeStamp": datetime.now().strftime("%Y-%m-%d"),
                    "categoryId": asset["category_id"],
                    "categoryName": asset["category_name"],
                    "categoryType": asset["category_type"],
                    "email": "support@northladder.com",
                    "groupId": asset["product_id"],
                    "isSellAsset": True,
                },
                headers=header,
                timeout=40,
            )

            if response.status_code == 200 and response.json().get("status") == True:
                data = response.json()
                for amount in data["data"]["quote"]:
                    for item in prices:
                        if web_name in item:
                            item[web_name].append(
                                {
                                    "condition": amount["condition"]["condition"],
                                    "condition_description": amount["condition"][
                                        "conditionDescription"
                                    ],
                                    "price": amount["sellAmount"]["sellAmount"],
                                    "bonus_amount": amount["bonusAmount"],
                                }
                            )
                logger.info(f"Got buyback prices for {web_name}.")
                break
            else:
                logger.warning(
                    f"Failed to get prices of products. Retrying... (get_buyback_individual_thread) - {failed_tries}"
                )
                failed_tries += 1

    try:
        # thread for individual site price
        threads = []
        prices = [{"northladder": []}, {"revibe": []}, {"revent": []}]
        for info in ["northladder", "revibe", "revent"]:
            thread = threading.Thread(
                target=get_buyback_individual_thread,
                args=(asset, info, prices),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        # saving prices to database
        db = connect_to_mongo()

        if db["buyback"].find_one({"asset_id": asset["asset_id"]}):
            db["buyback"].update_one(
                {"asset_id": asset["asset_id"]},
                {"$set": {"prices": prices, "updated_at": datetime.now()}},
            )
            logger.info(f"Updated buyback prices for {asset['product_name']}.")
        else:
            db["buyback"].insert_one(
                {
                    "asset_id": asset["asset_id"],
                    "product_name": asset["product_name"],
                    "brand_id": asset["brand_id"],
                    "brand_name": asset["brand_name"],
                    "category_id": asset["category_id"],
                    "category_name": asset["category_name"],
                    "category_type": asset["category_type"],
                    "properties": asset["properties"],
                    "prices": prices,
                    "updated_at": datetime.now(),
                }
            )
            logger.info(f"Inserted buyback prices for {asset['product_name']}.")

    except Exception as e:
        logger.error(
            f"Error in getting active buyback assets. Retrying... (get_buyback_prices) - {failed_tries}",
            exc_info=True,
        )
