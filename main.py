from fastapi import FastAPI

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

app = FastAPI()

@app.get('/')
async def root():
    return {'example': 'hello'}

@app.get('/getprices/{product}')
async def get_prices(product : str):
    url = f"https://www.nofrills.ca/search?search-bar={product}"
    driver = webdriver.Chrome()
    driver.get(url)

    # wait for page to load
    driver.maximize_window()
    driver.implicitly_wait(20)

    products = driver.find_elements(By.CLASS_NAME, "product-tracking")
    arr = []
    for product in products:
        products_html = product.get_attribute("innerHTML")
        soup = BeautifulSoup(products_html, 'html.parser')
        product_tiles = soup.find_all('div', class_='product-tile')

        for tile in product_tiles:
            # Find the price element
            price_element = tile.find('span', class_='price__value')
            if price_element:
                price = price_element.get_text(strip=True)

                # Find the product name element
                product_name_element = tile.find('span', class_='product-name__item--name')
                if product_name_element:
                    product_name = product_name_element.get_text(strip=True)
                    # print(f"Product: {product_name}")
                    arr.append(product_name)
                    # print(f"Price: {price}")
                    # print()
    # time.sleep(20)

    driver.quit()
    return {'products': arr}
