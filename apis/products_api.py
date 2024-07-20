from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from controllers.product_controller import (
    download_products,
    scrape_products,
    upload_products,
    get_live_product,
    get_product_description,
    get_product,
)

product_router = APIRouter()


# to download all products details from the database in csv
@product_router.get("/download-all")
async def download_products_route():
    return download_products()


# to update scrap data of existing products from the web
@product_router.get("/scrape-live")
async def scrape_products_route():
    return scrape_products()


# to upload product details from a file and save it to the database
@product_router.post("/upload")
async def upload_products_route(file: UploadFile, BackgroundTasks: BackgroundTasks):
    return await upload_products(file, BackgroundTasks)


# to scrape product details live from the web and update the database
@product_router.get("/live/{product_id}")
async def get_live_product_route(product_id):
    return get_live_product(product_id)


# to get bullet points, description and specifications of a product
@product_router.get("/get-description/{product_id}")
def get_product_description_route(product_id):
    return get_product_description(product_id)


# to get product details by product_id from database
@product_router.get("/{product_id}")
async def get_product_route(product_id):
    return get_product(product_id)
