import re

# to transform product name with amazon search format
def transform_name(name):
    # Remove special characters and replace them with spaces
    name = re.sub(r"[^\w\s]", " ", name)
    # Replace multiple spaces with a single space
    name = re.sub(r"\s+", " ", name)
    # Remove leading and trailing spaces
    name = name.strip()
    # Replace specific patterns with spaces
    name = re.sub(r"\s?-\s?", " ", name)
    name = re.sub(r"\s?/\s?", " ", name)
    # Add space between digits and units (GB, TB, etc.)
    name = re.sub(r"(\d+)\s?([GB|TB|MB])", r"\1 \2", name)
    # Remove extra spaces around numbers
    name = re.sub(r"\s+(\d+)\s+", r" \1 ", name)

    return name


# transform name with noon url format
def transform_noon_url_name(name):
    # Remove space between numbers and units
    transformed_name = re.sub(r"(\d+)\s+(GB|MB|TB)", r"\1\2", name)
    return transformed_name


# to format category name
def transform_category(category):
    if type(category) != str:
        return []
    return [part.strip() for part in category.split("/")]


# to format category name for csv file
def transform_category_csv(category):
    return "/".join(category)