from fastapi import FastAPI
from apis.products_api import product_router
from apis.popsy_api import popsy_router

app = FastAPI()


# include routes from products and popsy
app.include_router(product_router, tags=["product"], prefix="/product")
app.include_router(popsy_router, tags=["popsy"], prefix="/popsy")

# root route
@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello! This is R3 Factory"}
