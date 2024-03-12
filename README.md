# Ecom Scraper

Ecom Scraper is a Python project for scraping product details from e-commerce websites like Amazon, Noon, and Cartlow.
It allows you to extract product information such as title, price, rating, and description, and store it in a structured format for further analysis.

![Python](https://img.shields.io/badge/python-blue.svg?style=for-the-badge&logo=python&logoColor=white)


## Setup

```
Step 1: Clone this repository

$ git clone https://github.com/var-rishabh/ecom-scraper.git
```

```
Step 2: Setup the virtual environment and activate it

$ cd finaccru-web

$ python -m venv venv

$ ./venv/Scripts/activate
```

```
Step 3: Install the required Python packages

$ pip install -r requirements.txt
```


## Usage

```
Step 1: Add product names to the data/products_names.txt file, each on a new line.
```

```
Step 2: Run the scrape.py script to start scraping

$ python scrape.py
```

```
Step 3: The scraped data will be saved in the outputs directory in JavaScript format (result.js).
```

## Adding More Products
To add more products to the scraping list, simply append the product names to the `data/products_names.txt` file and rerun the `scrape.py` script. 

The new products data will be appended to the existing `result.js` file in outputs folder.

> Note: You can find the HTML file of all the products page fetched from the web in `data/HTMl` folder to verify the scraped information.