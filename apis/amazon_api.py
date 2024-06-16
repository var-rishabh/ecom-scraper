from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from controllers.amazon_controller import (
    amazon_asin,
    amazon_csv,
    amazon_books,
    amazon_books_csv,
)

amazon_router = APIRouter()


# to get amazon data in csv format
@amazon_router.get("/amazon-csv")
async def amazon_csv_route():
    return amazon_csv()


# to get amazon data using ASIN number
@amazon_router.post("/amazon-asin")
async def amazon_asin_route(file: UploadFile, BackgroundTasks: BackgroundTasks):
    return await amazon_asin(file, BackgroundTasks)


# to get amazon books data in csv format
@amazon_router.get("/amazon-books-csv")
async def amazon_books_csv_route():
    return amazon_books_csv()


# to get amazon books data using ASIN number
@amazon_router.post("/amazon-books")
async def amazon_books_route(file: UploadFile, BackgroundTasks: BackgroundTasks):
    return await amazon_books(file, BackgroundTasks)
