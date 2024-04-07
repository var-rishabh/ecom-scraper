from fastapi import APIRouter, BackgroundTasks
from controllers.revibe_controller import scrape_all_products

revibe_router = APIRouter()


# to scrape all products details from the web
@revibe_router.get("/scrape-all")
async def scrape_all_products_route(BackgroundTasks: BackgroundTasks):
    return scrape_all_products(BackgroundTasks)
