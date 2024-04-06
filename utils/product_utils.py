from config.logger import logger


# to format product collection for search
def transform_products(products):
    try:
        all_products = []
        for product in products:
            all_products.append(
                {
                    "product_id": product["product_id"],
                    "brand": product["brand"],
                    "name": product["name"],
                    "search_name": f'{product["brand"]} {product["name"]}',
                    "category": product["category"],
                    "amazon": product["amazon"],
                    "cartlow": product["cartlow"],
                    "noon": product["noon"],
                }
            )
        return all_products

    except Exception as e:
        logger.error(f"Error transforming products.", exc_info=True)
        return []
