# to format product collection for search
def transform_products(products):
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
