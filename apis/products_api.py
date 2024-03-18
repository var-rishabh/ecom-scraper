from fastapi import APIRouter, File, UploadFile
from controllers.product_controller import (
    get_all_products,
    download_products,
    scrape_products,
    upload_products,
    get_live_product,
    get_product,
)

router = APIRouter()


# to get all products details from the database
@router.get("/get-all")
async def get_all_products_route():
    return get_all_products()


# to download all products details from the database in csv
@router.get("/download-all")
async def download_products_route():
    return download_products()


# to update scrap data of existing products from the web
@router.get("/scrape-live")
async def scrape_products_route():
    return scrape_products()


# to upload product details from a file and save it to the database
@router.post("/upload")
async def upload_products_route(file: UploadFile):
    return await upload_products(file)


# to scrape product details live from the web and update the database
@router.get("/live/{product_id}")
async def get_live_product_route(product_id: int):
    return get_live_product(product_id)


# to get product details by product_id from database
@router.get("/{product_id}")
async def get_product_route(product_id: int):
    return get_product(product_id)