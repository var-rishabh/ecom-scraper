import csv
from io import StringIO

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

from config.db import connect_to_mongo
from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scrape import scrape_all, scrape_amazon_with_asin

from utils.file_utils import get_file_data, get_amazon_asin_file_data


# to download all amazon products with asin number in csv from database
def amazon_csv():
    db = connect_to_mongo()

    try:
        products = db["amazon"].find({})

        filename = "amazon_asin_data.csv"
        header = [
            "asin_number",
            "name",
            "discount_price",
            "list_price",
            "seller",
            "rating",
            "number_of_reviews",
            "grade",
            "url",
            "description",
            "images",
        ]

        all_products = []
        for product in products:
            if "name" in product and product["name"] is None:
                pass
            else:
                data = {
                    "asin_number": product["asin_number"],
                    "name": product["name"],
                    "discount_price": product["discount_price"],
                    "list_price": product["list_price"],
                    "seller": product["seller"],
                    "rating": product["rating"],
                    "number_of_reviews": product["number_of_reviews"],
                    "grade": product["grade"],
                    "url": product["url"],
                    "description": product["bullet_points"],
                    "images": product["images"],
                }
                all_products.append(data)

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(header)
        for product in all_products:
            csv_writer.writerow(
                [
                    product["asin_number"],
                    product["name"],
                    product["discount_price"],
                    product["list_price"],
                    product["seller"],
                    product["rating"],
                    product["number_of_reviews"],
                    product["grade"],
                    product["url"],
                    product["description"],
                    product["images"],
                ]
            )

        csv_data.seek(0)
        logger.info("Products data downloaded successfully.")

        return StreamingResponse(
            iter([csv_data.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )

    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        return ErrorResponseModel(500, "An error occurred.", "Internal server error.")


# to get product info from amazon asin number
async def amazon_asin(file, background_tasks: BackgroundTasks):
    try:
        if file.filename.endswith((".csv", ".xlsx", ".xls")):
            data = await file.read()
            file_data = get_amazon_asin_file_data(data, file.filename)
            if not file_data:
                logger.error("File is empty.")
                return ErrorResponseModel(400, "An error occurred.", "File is empty.")

            background_tasks.add_task(scrape_amazon_with_asin, file_data)

            return ResponseModel(
                "Products data scraping in running background. It will take time.", None
            )
        else:
            logger.error("File type not supported.")
            return ErrorResponseModel(
                400, "An error occurred.", "File type not supported."
            )

    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        return ErrorResponseModel(500, "An error occurred.", "Internal server error.")
