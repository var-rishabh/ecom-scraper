import os
import json

def read_product_names(file_path):
    with open(file_path, "r") as file:
        product_names = [line.strip() for line in file.readlines()]
        return product_names


def save_data_to_js_file(data):
    with open("outputs/result.js", "w") as file:
        file.write(f"const data = {json.dumps(data, indent=2)};")


def save_data_to_html_file(product_name, site_name, data):
    folder = f"data/HTML/{product_name}"
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    site_folder = f"{folder}/{site_name}"
    if not os.path.exists(site_folder):
        os.makedirs(site_folder)
        
    file_name = f"{site_folder}/link{len(os.listdir(site_folder))+1}.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(data)