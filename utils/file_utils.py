import os
import csv
import pandas as pd
from io import StringIO

from utils.name_utils import transform_name, transform_category


# to extract product_id, brand, name and category from the csv or xlsx file
def get_file_data(file_data, file_name):
    data = None
    if file_name.endswith(".csv"):
        data = pd.read_csv(StringIO(file_data.decode('utf-8')))
    elif file_name.endswith((".xlsx", ".xls")):
        data = pd.read_excel(file_data)

    products = []
    for index, row in data.iterrows():
        if type(row["brand_name"]) == float and pd.isnull(row["brand_name"]):
            row["brand_name"] = ""
        if type(row["model_number"]) == float and pd.isnull(row["model_number"]):
            row["model_number"] = ""
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


# to extract amazon asin number from the csv or xlsx file
def get_amazon_asin_file_data(file_data, file_name):
    data = None
    asin_numbers = []
    
    if file_name.endswith(".csv"):
        decoded_content = file_data.decode("utf-8")
        data = csv.reader(StringIO(decoded_content))
        header = next(data)
        for row in data:
            row = ", ".join(row)
            asin_numbers.append(row)
    elif file_name.endswith((".xlsx", ".xls")):
        data = pd.read_excel(file_data)
        for index, row in data.iterrows():
            asin_numbers.append(row["asin_number"])

    return asin_numbers


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
