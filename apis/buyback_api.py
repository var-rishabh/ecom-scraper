from fastapi import APIRouter, BackgroundTasks
from controllers.buyback_controller import (
    scrape_all_prices,
    northladder_prices,
    scrape_cartlow_prices,
    download_cartlow_prices,
)

buyback_router = APIRouter()


# to scrape all prices details from the Northladder, Revent and Revibe
@buyback_router.get("/scrape-all-prices")
async def scrape_all_prices_route(BackgroundTasks: BackgroundTasks):
    return scrape_all_prices(BackgroundTasks)


# to scrape all prices details from the Northladder
@buyback_router.get("/northladder-prices")
async def northladder_prices_route():
    return northladder_prices()


# to scrape all prices of products from cartlow sell section
@buyback_router.get("/scrape-cartlow-prices")
async def scrape_cartlow_prices_route(BackgroundTasks: BackgroundTasks):
    return scrape_cartlow_prices(BackgroundTasks)


# to download prices of products from cartlow sell section
@buyback_router.get("/download-cartlow-prices")
async def download_cartlow_prices_route():
    return download_cartlow_prices()
