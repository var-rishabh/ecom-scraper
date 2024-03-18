from pydantic import BaseModel, Field, validator
from typing import List, Optional, ClassVar


class ProductModel(BaseModel):
    product_id: int = Field(..., description="Unique identifier for the product")
    name: str = Field(..., description="Name of the product")
    brand: str = Field(..., description="Brand of the product")
    category: List[str] = Field(..., description="Category of the product")
    amazon: Optional[List[dict]] = []
    cartlow: Optional[List[dict]] = []
    noon: Optional[List[dict]] = []
    updated_on: str = Field(..., description="Date and time of the last update")
    @validator("product_id")
    def check_product_id(cls, v):
        if v in cls.used_product_ids:
            raise ValueError("product_id must be unique")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 10000,
                "name": "Product Name",
                "brand": "Brand Name",
                "category": ["Category 1", "Category 2"],
                "amazon": [
                    {"name": "Amazon", "price": 100, "url": "https://www.amazon.com"}
                ],
                "cartlow": [
                    {"name": "Cartlow", "price": 100, "url": "https://www.cartlow.com"},
                    {"name": "Cartlow", "price": 100, "url": "https://www.cartlow.com"},
                ],
                "noon": [],
                "updated_on": "2024-03-01T12:00:00",
            }
        }

    used_product_ids: ClassVar[set] = set()


# response model
def ResponseModel(message, data):
    return {
        "status": 200,
        "message": message,
        "data": [data],
    }


# error response model
def ErrorResponseModel(status, error, message):
    return {"status": status, "error": error, "message": message}
