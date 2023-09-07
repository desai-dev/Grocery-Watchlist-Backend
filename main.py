from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import os
from twilio.rest import Client

from dotenv import load_dotenv
load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
TO_NUMBER = os.getenv("TO_NUMBER")
FROM_NUMBER = os.getenv("FROM_NUMBER")


class Product(BaseModel):
    id: str
    name: str
    price: str
    watchPrice: str 

app = FastAPI()

# Configure CORS
origins = ["http://localhost:4200"]  # Update this with your Angular app's URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    dic = {}
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
                    dic[product_name] = price
                    # print(f"Product: {product_name}")
                    # print(f"Price: {price}")
                    # print()
    # time.sleep(20)

    driver.quit()
    return dic

@app.post('/scrapewatchlist')
async def scrape_watchlist(product: Product):
    products = await get_prices(product.name)
    print(products)
    if products[product.name] <= product.watchPrice:
        send_notification(product.name, products[product.name])
    return [product.name, products[product.name]]

def send_notification(product, price):
    # Your Account SID from twilio.com/console
    account_sid = ACCOUNT_SID
    # Your Auth Token from twilio.com/console
    auth_token  = AUTH_TOKEN

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=TO_NUMBER, 
        from_=FROM_NUMBER,
        body=f"${product} now has a price of ${price}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# uvicorn main:app --reload