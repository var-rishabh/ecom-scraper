import csv
from io import StringIO

from fastapi import BackgroundTasks
from fastapi.responses import StreamingResponse

from config.db import connect_to_mongo
from models.response import ResponseModel, ErrorResponseModel
from scraper.scrape import scrape_all
from utils.file_utils import get_file_data
from utils.product_utils import transform_products
from utils.name_utils import transform_category_csv


# to get all products details from the database
def get_all_products():
    db = connect_to_mongo()

    products = []
    for prod in db["products"].find({}, {"_id": 0}):
        products.append(prod)

    return ResponseModel("Products data found successfully.", products)


# to download all products details from the database in csv
def download_products():
    db = connect_to_mongo()

    products = db["products"].find({}).sort({"product_id": 1})

    filename = "products.csv"
    header = [
        "product_id",
        "brand",
        "name",
        "category",
        "amazon_asin_number",
        "amazon_price",
        "cartlow_price",
        "noon_price",
        "amazon_seller",
        "cartlow_seller",
        "noon_seller",
        "amazon_rating",
        "cartlow_rating",
        "noon_rating",
        "amazon_number_of_reviews",
        "cartlow_number_of_reviews",
        "noon_number_of_reviews",
        "amazon_url",
        "cartlow_url",
        "noon_url",
        "amazon_grade",
        "cartlow_grade",
        "noon_grade",
    ]

    all_products = []
    for product in products:
        data = {}
        data["product_id"] = product["product_id"]
        data["brand"] = product["brand"]
        data["name"] = product["name"]
        data["category"] = transform_category_csv(product["category"])
        if not product["amazon"]:
            product["amazon"] = [{}]
        if not product["cartlow"]:
            product["cartlow"] = [{}]
        if not product["noon"]:
            product["noon"] = [{}]

        for amazon_data in product["amazon"]:
            data["amazon_price"] = (
                amazon_data["discount_price"]
                if "discount_price" in amazon_data
                else "NA"
            )
            data["amazon_asin_number"] = (
                amazon_data["asin_number"] if "asin_number" in amazon_data else "NA"
            )
            data["amazon_seller"] = (
                amazon_data["seller"] if "seller" in amazon_data else "NA"
            )
            data["amazon_rating"] = (
                amazon_data["rating"] if "rating" in amazon_data else "NA"
            )
            data["amazon_number_of_reviews"] = (
                amazon_data["number_of_reviews"]
                if "number_of_reviews" in amazon_data
                else "NA"
            )
            data["amazon_grade"] = (
                amazon_data["grade"] if "grade" in amazon_data else "NA"
            )
            data["amazon_url"] = amazon_data["url"] if "url" in amazon_data else "NA"
            break
        for cartlow_data in product["cartlow"]:
            data["cartlow_price"] = (
                cartlow_data["discount_price"]
                if "discount_price" in cartlow_data
                else "NA"
            )
            data["cartlow_seller"] = (
                cartlow_data["seller"] if "seller" in cartlow_data else "NA"
            )
            data["cartlow_rating"] = (
                cartlow_data["rating"] if "rating" in cartlow_data else "NA"
            )
            data["cartlow_number_of_reviews"] = (
                cartlow_data["number_of_reviews"]
                if "number_of_reviews" in cartlow_data
                else "NA"
            )
            data["cartlow_grade"] = (
                cartlow_data["grade"] if "grade" in cartlow_data else "NA"
            )
            data["cartlow_url"] = cartlow_data["url"] if "url" in cartlow_data else "NA"
            break
        for noon_data in product["noon"]:
            data["noon_price"] = (
                noon_data["discount_price"] if "discount_price" in noon_data else "NA"
            )
            data["noon_seller"] = noon_data["seller"] if "seller" in noon_data else "NA"
            data["noon_rating"] = noon_data["rating"] if "rating" in noon_data else "NA"
            data["noon_number_of_reviews"] = (
                noon_data["number_of_reviews"]
                if "number_of_reviews" in noon_data
                else "NA"
            )
            data["noon_grade"] = noon_data["grade"] if "grade" in noon_data else "NA"
            data["noon_url"] = noon_data["url"] if "url" in noon_data else "NA"
            break
        all_products.append(data)

    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(header)
    for product in all_products:
        csv_writer.writerow(
            [
                product["product_id"],
                product["brand"],
                product["name"],
                product["category"],
                product["amazon_asin_number"],
                product["amazon_price"],
                product["cartlow_price"],
                product["noon_price"],
                product["amazon_seller"],
                product["cartlow_seller"],
                product["noon_seller"],
                product["amazon_rating"],
                product["cartlow_rating"],
                product["noon_rating"],
                product["amazon_number_of_reviews"],
                product["cartlow_number_of_reviews"],
                product["noon_number_of_reviews"],
                product["amazon_url"],
                product["cartlow_url"],
                product["noon_url"],
                product["amazon_grade"],
                product["cartlow_grade"],
                product["noon_grade"],
            ]
        )

    csv_data.seek(0)
    return StreamingResponse(
        iter([csv_data.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )


# to update scrap data of existing products from the web
def scrape_products():
    db = connect_to_mongo()

    products = db["products"].find({})
    products = transform_products(products)

    scraped_data = scrape_all(products)

    return ResponseModel("Products data updated successfully.", scraped_data)


# to upload product details from a file and save it to the database
async def upload_products(file, background_tasks: BackgroundTasks):
    if file.filename.endswith((".csv", ".xlsx", ".xls")):
        data = await file.read()
        file_data = get_file_data(data, file.filename)
        if not file_data:
            return ErrorResponseModel(400, "An error occurred.", "File is empty.")

        background_tasks.add_task(scrape_all, file_data)

        return ResponseModel("Products data scraping in running background. It will take time.", None)
    else:
        return ErrorResponseModel(400, "An error occurred.", "File type not supported.")


# to scrape product details live from the web and update the database
def get_live_product(product_id: int):
    db = connect_to_mongo()

    product_data = db["products"].find_one({"product_id": product_id}, {"_id": 0})
    products = transform_products([product_data])

    scraped_data = scrape_all(products)

    return ResponseModel("Products data updated successfully.", scraped_data)


# to get product details by product_id from database
def get_product(product_id: int):
    db = connect_to_mongo()

    product_data = db["products"].find_one({"product_id": product_id}, {"_id": 0})
    if not product_data:
        return ErrorResponseModel(404, "An error occurred.", "Product not found.")

    filename = f'{product_data["product_id"]}.csv'
    header = [
        "product_id",
        "brand",
        "name",
        "category",
        "amazon_asin_number",
        "amazon_price",
        "cartlow_price",
        "noon_price",
        "amazon_seller",
        "cartlow_seller",
        "noon_seller",
        "amazon_rating",
        "cartlow_rating",
        "noon_rating",
        "amazon_number_of_reviews",
        "cartlow_number_of_reviews",
        "noon_number_of_reviews",
        "amazon_url",
        "cartlow_url",
        "noon_url",
        "amazon_grade",
        "cartlow_grade",
        "noon_grade",
    ]

    data = {}
    data["product_id"] = product_data["product_id"]
    data["brand"] = product_data["brand"]
    data["name"] = product_data["name"]
    data["category"] = transform_category_csv(product_data["category"])
    if not product_data["amazon"]:
        product_data["amazon"] = [{}]
    if not product_data["cartlow"]:
        product_data["cartlow"] = [{}]
    if not product_data["noon"]:
        product_data["noon"] = [{}]

    for amazon_data in product_data["amazon"]:
        data["amazon_price"] = (
            amazon_data["discount_price"] if "discount_price" in amazon_data else "NA"
        )
        data["amazon_asin_number"] = (
            amazon_data["asin_number"] if "asin_number" in amazon_data else "NA"
        )
        data["amazon_seller"] = (
            amazon_data["seller"] if "seller" in amazon_data else "NA"
        )
        data["amazon_rating"] = (
            amazon_data["rating"] if "rating" in amazon_data else "NA"
        )
        data["amazon_number_of_reviews"] = (
            amazon_data["number_of_reviews"]
            if "number_of_reviews" in amazon_data
            else "NA"
        )
        data["amazon_grade"] = amazon_data["grade"] if "grade" in amazon_data else "NA"
        data["amazon_url"] = amazon_data["url"] if "url" in amazon_data else "NA"
        break
    for cartlow_data in product_data["cartlow"]:
        data["cartlow_price"] = (
            cartlow_data["discount_price"] if "discount_price" in cartlow_data else "NA"
        )
        data["cartlow_seller"] = (
            cartlow_data["seller"] if "seller" in cartlow_data else "NA"
        )
        data["cartlow_rating"] = (
            cartlow_data["rating"] if "rating" in cartlow_data else "NA"
        )
        data["cartlow_number_of_reviews"] = (
            cartlow_data["number_of_reviews"]
            if "number_of_reviews" in cartlow_data
            else "NA"
        )
        data["cartlow_grade"] = (
            cartlow_data["grade"] if "grade" in cartlow_data else "NA"
        )
        data["cartlow_url"] = cartlow_data["url"] if "url" in cartlow_data else "NA"
        break
    for noon_data in product_data["noon"]:
        data["noon_price"] = (
            noon_data["discount_price"] if "discount_price" in noon_data else "NA"
        )
        data["noon_seller"] = noon_data["seller"] if "seller" in noon_data else "NA"
        data["noon_rating"] = noon_data["rating"] if "rating" in noon_data else "NA"
        data["noon_number_of_reviews"] = (
            noon_data["number_of_reviews"] if "number_of_reviews" in noon_data else "NA"
        )
        data["noon_grade"] = noon_data["grade"] if "grade" in noon_data else "NA"
        data["noon_url"] = noon_data["url"] if "url" in noon_data else "NA"
        break

    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(header)
    csv_writer.writerow(
        [
            data["product_id"],
            data["brand"],
            data["name"],
            data["category"],
            data["amazon_asin_number"],
            data["amazon_price"],
            data["cartlow_price"],
            data["noon_price"],
            data["amazon_seller"],
            data["cartlow_seller"],
            data["noon_seller"],
            data["amazon_rating"],
            data["cartlow_rating"],
            data["noon_rating"],
            data["amazon_number_of_reviews"],
            data["cartlow_number_of_reviews"],
            data["noon_number_of_reviews"],
            data["amazon_url"],
            data["cartlow_url"],
            data["noon_url"],
            data["amazon_grade"],
            data["cartlow_grade"],
            data["noon_grade"],
        ]
    )

    csv_data.seek(0)
    return StreamingResponse(
        iter([csv_data.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )
