import requests

def generate_search_urls(product_names):
    amazon_urls = [
        f'https://www.amazon.ae/s?k={"+".join(product_name.split())}'
        for product_name in product_names
    ]

    return amazon_urls


def generate_amazon_search_urls(amazon_urls):
    global visited_urls
    response = requests.get(listing_url, headers=custom_headers)
    print(response.status_code)
    soup_search = BeautifulSoup(response.text, "lxml")
    link_elements = soup_search.select("[data-asin] h2 a")
    page_data = []

    for link in link_elements:
        full_url = urljoin(listing_url, link.attrs.get("href"))
        if full_url not in visited_urls:
            visited_urls.add(full_url)
            print(f"Scraping product from {full_url[:100]}", flush=True)
            product_info = get_product_info(full_url)
            if product_info:
                page_data.append(product_info)

    next_page_el = soup_search.select_one("a.s-pagination-next")
    if next_page_el:
        next_page_url = next_page_el.attrs.get("href")
        next_page_url = urljoin(listing_url, next_page_url)
        print(f"Scraping next page: {next_page_url}", flush=True)
        page_data += parse_listing(next_page_url)

    return page_data
