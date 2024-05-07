from fastapi import APIRouter, BackgroundTasks
from controllers.buyback_controller import scrape_all_prices

buyback_router = APIRouter()


# to scrape all prices details from the Northladder, Revent and Revibe
@buyback_router.get("/scrape-all-prices")
async def scrape_all_prices_route(BackgroundTasks: BackgroundTasks):
    return scrape_all_prices(BackgroundTasks)
