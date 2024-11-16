from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from backend.logger import logger

from api.utils.web_driver import get_driver, quit_driver
import time


def scrape_comfy_product(product_name):
    driver = get_driver()

    # URL for searching the product on Comfy
    # search_url = f"https://comfy.ua/search/?q={product_name.replace(' ', '%20')}"
    # driver.get(search_url)
    # time.sleep(5)

    driver.get('https://comfy.ua/')
    time.sleep(3)

    search_input = driver.find_element(By.XPATH, '//input[@name="q"]')
    search_input.send_keys(product_name + Keys.ENTER)
    time.sleep(3)

    try:
        # Find the product link (Comfy uses 'product-item__name' for product headings)
        product_link = driver.find_element(By.CLASS_NAME, 'prdl-item__name').get_attribute('href')
        logger.info(f"Found product link: {product_link}")
        # product_link.click()

        # Scrape the product details
        product_details = scrape_comfy_product_details(driver, product_link)

    finally:
        quit_driver()

    return product_details


def scrape_comfy_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)

    # Extract product name and price
    product_name = driver.find_element(By.CLASS_NAME, 'gen-tab__name').text.strip()
    product_price = driver.find_element(By.CLASS_NAME, 'price__current').text.strip()

    # print(f"Scraped product: {product_name}, Price: {product_price}")

    # Comfy may not have reviews like Rozetka, so we'll return an empty reviews list for now
    reviews = scrape_comfy_reviews(driver, product_url)

    return {
        'name': product_name,
        'price': product_price,
        'url': product_url,
        'reviews': reviews
    }


def scrape_comfy_reviews(driver, product_url):
    # Assume that reviews might be found under a section; for now, we'll return an empty list
    # Placeholder in case you want to add review scraping later
    reviews = []

    # Check if there is a review section (adapt based on actual HTML structure)
    try:
        review_elements = driver.find_elements(By.CSS_SELECTOR, '#feedback .r-item')
        for review_element in review_elements:
            review_text = review_element.find_element(By.CLASS_NAME, 'r-item__text').text.strip()

            # Assume rating is stored in some form
            review_rating_element = review_element.find_element(By.CLASS_NAME, 'rating-box__active')
            rating_style = review_rating_element.get_attribute('style')
            rating_percentage = float(rating_style.split('width:')[1].replace('%;', '').strip())
            review_rating = (rating_percentage / 100) * 5

            reviews.append({
                'text': review_text,
                'rating': round(review_rating, 1)
            })

        logger.info(f"Scraped {len(reviews)} valid reviews with ratings.")

    except NoSuchElementException:
        logger.warn("No reviews found.")

    return reviews
