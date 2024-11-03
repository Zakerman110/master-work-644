from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

from api.utils.web_driver import get_driver
from api.utils.db_utils import save_product_to_db
from api.models import Product

# https://www.foxtrot.com.ua/uk/search?query=iPhone%2012
# https://allo.ua/ua/catalogsearch/result/?q=iPhone%2012
# https://comfy.ua/search/?q=iPhone%2012
# https://www.ctrs.com.ua/ru/search/?query=iPhone%2012

def scrape_rozetka_product(product_name):
    driver = get_driver()

    search_url = f"https://rozetka.com.ua/search/?text={product_name.replace(' ', '%20')}"
    driver.get(search_url)

    time.sleep(3)

    try:
        product_link = driver.find_element(By.CLASS_NAME, 'goods-tile__heading').get_attribute('href')
        print(f"Found product link: {product_link}")

        product_details = scrape_rozetka_product_details(driver, product_link)

    finally:
        driver.quit()

    return product_details


def scrape_rozetka_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)

    product_name = driver.find_element(By.TAG_NAME, 'h1').text.strip()
    product_price = driver.find_element(By.CLASS_NAME, 'product-price__big').text.strip()

    # print(f"Scraped product: {product_name}, Price: {product_price}")

    reviews = scrape_rozetka_reviews(driver, product_url)

    return {
        'name': product_name,
        'price': product_price,
        'url': product_url,
        'reviews': reviews
    }


def scrape_rozetka_reviews(driver, product_url):
    reviews_url = product_url + 'comments/'
    driver.get(reviews_url)
    time.sleep(3)

    reviews = []

    review_elements = driver.find_elements(By.CLASS_NAME, 'r-item__content')
    for review_element in review_elements:
        try:
            review_text = review_element.find_element(By.CLASS_NAME, 'r-item__text').text.strip()

            review_rating_element = review_element.find_element(By.CLASS_NAME, 'rating-box__active')
            rating_style = review_rating_element.get_attribute('style')
            rating_percentage = float(rating_style.split('width:')[-1].replace('%', ''))
            review_rating = (rating_percentage / 100) * 5

            reviews.append({
                'text': review_text,
                'rating': round(review_rating, 1)
            })

        except NoSuchElementException:
            print("No rating found for this review, skipping.")
            continue

    print(f"Scraped {len(reviews)} valid reviews with ratings.")
    return reviews

