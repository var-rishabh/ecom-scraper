import os
import pandas as pd

from utils.name_utils import transform_name, transform_category


# to extract product_id, brand, name and category from the csv or xlsx file
def get_file_data(file_data, file_name):
    data = None
    if file_name.endswith(".csv"):
        data = read_csv(file_data)
    elif file_name.endswith((".xlsx", ".xls")):
        data = pd.read_excel(file_data)

    products = []
    for index, row in data.iterrows():
        if type(row["brand_name"]) == float and pd.isnull(row["brand_name"]):
            row["brand_name"] = ""
        product_info = {
            "product_id": row["product_id"],
            "brand": row["brand_name"],
            "name": row["product_name"],
            "model": row["model_number"],
            "search_name": transform_name(f'{row["brand_name"]} {row["product_name"]}'),
            "category": transform_category(row["category"]),
        }
        if (
            row["brand_name"] == "FALSE"
            or row["brand_name"] == "False"
            or row["brand_name"] == False
        ):
            product_info["brand"] = ""
            product_info["search_name"] = transform_name(f'{row["product_name"]}')
        elif row["brand_name"] == "generic" or row["brand_name"] == "Generic":
            product_info["brand"] = "Generic"
            product_info["search_name"] = transform_name(f'{row["product_name"]}')
        products.append(product_info)

    return products


# saving the scraped html page to a file
def save_data_to_html_file(product_name, site_name, file_name, data):
    folder = f"data/HTML/{product_name}"
    if not os.path.exists(folder):
        os.makedirs(folder)

    site_folder = f"{folder}/{site_name}"
    if not os.path.exists(site_folder):
        os.makedirs(site_folder)

    file_name = f"{site_folder}/{file_name}.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data)


# deleting the existing file in the folder
def delete_file(product_name, site_name, file_name):
    file_path = f"data/HTML/{product_name}/{site_name}/{file_name}"
    if os.path.exists(file_path):
        os.remove(file_path)
