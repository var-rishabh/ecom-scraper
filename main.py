from fastapi import FastAPI
from apis.products_api import router

app = FastAPI()


# include the router from products_api.py
app.include_router(router, tags=["product"], prefix="/product")


# root route
@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello! This is R3 Factory"}
