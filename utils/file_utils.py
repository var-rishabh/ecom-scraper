import json


def read_product_names(file_path):
    with open(file_path, "r") as file:
        product_names = [line.strip() for line in file.readlines()]
        return product_names


def save_data_to_js_file(data):
    with open("outputs/data.js", "w") as file:
        file.write("const data = [\n")
        for product_name, sites_data in data.items():
            file.write("  {\n")
            file.write(f"    '{product_name}': [\n")
            for site_name, products_data in sites_data.items():
                file.write("      {\n")
                for key, value in products_data.items():
                    if isinstance(value, list):
                        file.write(f"        {key}: {json.dumps(value)},\n")
                    elif isinstance(value, dict):
                        file.write(f"        {key}: {json.dumps(value, indent=2)},\n")
                    else:
                        file.write(f"        {key}: '{value}',\n")
                file.write("      },\n")
            file.write("    ],\n")
            file.write("  },\n")
        file.write("];\n")
