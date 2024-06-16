import csv
from io import StringIO

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

from config.db import connect_to_mongo
from config.logger import logger

from models.response import ResponseModel, ErrorResponseModel
from scraper.scrape import scrape_all, scrape_amazon_with_asin, scrape_amazon_books

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

                if (
                    "multiple_vendors" in product
                    and product["multiple_vendors"] is not None
                ):
                    for vendor in product["multiple_vendors"]:
                        data = {
                            "asin_number": product["asin_number"],
                            "name": product["name"],
                            "discount_price": vendor["vendor_discount_price"],
                            "list_price": vendor["vendor_list_price"],
                            "seller": vendor["vendor_name"],
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


# to download all amazon books with asin number in csv from database
def amazon_books_csv():
    db = connect_to_mongo()

    try:
        books = db["books"].find({})

        filename = "amazon_books.csv"
        header = [
            "asin_number",
            "title",
            "subtitle",
            "hardcover_price",
            "paperback_price",
            "publisher",
            "published_date",
            "authors",
            "categories",
            "language",
            "url",
            "info_link",
            "images",
            "description",
            "isbn_10",
        ]

        all_books = []
        for book in books:
            if "title" in book and book["title"] is None:
                pass
            else:
                data = {
                    "asin_number": book["asin_number"],
                    "title": book["title"],
                    "subtitle": book["subtitle"] if "subtitle" in book and book["subtitle"] is not None else "",
                    "hardcover_price": book["hardcover_price"],
                    "paperback_price": book["paperback_price"],
                    "publisher": book["publisher"] if "publisher" in book and book["publisher"] is not None else "",
                    "published_date": book["published_date"] if "published_date" in book and book["published_date"] is not None else "",
                    "authors": ", ".join(book["authors"]) if "authors" in book and book["authors"] is not None else "",
                    "categories": ", ".join(book["categories"]) if "categories" in book and book["categories"] is not None else "",
                    "language": book["language"] if "language" in book and book["language"] is not None else "",
                    "url": book["url"],
                    "info_link": book["info_link"] if "info_link" in book and book["info_link"] is not None else "",
                    "images": book["images"],
                    "description": book["description"] if "description" in book and book["description"] is not None else "",
                    "isbn_10": book["isbn_10"] if "isbn_10" in book and book["isbn_10"] is not None else "",
                }
                all_books.append(data)

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(header)
        for book in all_books:
            csv_writer.writerow(
                [
                    book["asin_number"],
                    book["title"],
                    book["subtitle"],
                    book["hardcover_price"],
                    book["paperback_price"],
                    book["publisher"],
                    book["published_date"],
                    book["authors"],
                    book["categories"],
                    book["language"],
                    book["url"],
                    book["info_link"],
                    book["images"],
                    book["description"],
                    book["isbn_10"]
                ]
            )

        csv_data.seek(0)
        logger.info("Books data downloaded successfully.")

        return StreamingResponse(
            iter([csv_data.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"},
        )

    except Exception as e:
        logger.error("Error occurred", exc_info=True)
        return ErrorResponseModel(500, "An error occurred.", "Internal server error.")


# to get product info from amazon asin number
async def amazon_books(file, background_tasks: BackgroundTasks):
    try:
        if file.filename.endswith((".csv", ".xlsx", ".xls")):
            data = await file.read()
            file_data = get_amazon_asin_file_data(data, file.filename)
            if not file_data:
                logger.error("File is empty.")
                return ErrorResponseModel(400, "An error occurred.", "File is empty.")

            background_tasks.add_task(scrape_amazon_books, file_data)

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
