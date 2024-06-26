from fastapi import FastAPI

from apis.amazon_api import amazon_router
from apis.buyback_api import buyback_router
from apis.products_api import product_router
from apis.popsy_api import popsy_router
from apis.revent_api import revent_router
from apis.revibe_api import revibe_router

app = FastAPI()


# routes
app.include_router(amazon_router, tags=["amazon"], prefix="/amazon")
app.include_router(buyback_router, tags=["buyback"], prefix="/buyback")
app.include_router(product_router, tags=["product"], prefix="/product")
app.include_router(popsy_router, tags=["popsy"], prefix="/popsy")
app.include_router(revent_router, tags=["revent"], prefix="/revent")
app.include_router(revibe_router, tags=["revibe"], prefix="/revibe")


# root route
@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello! This is R3 Factory"}
