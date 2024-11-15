from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from backend.logger import logger

from api.utils.web_driver import get_driver, quit_driver


def scrape_rozetka_suggestions(product_name):
    """
    Scrape search suggestions for a given product name on Rozetka.
    """
    driver = get_driver()

    # search_url = f"https://rozetka.com.ua/search/?text={product_name.replace(' ', '%20')}"
    # driver.get(search_url)
    driver.get('https://rozetka.com.ua/search/')
    time.sleep(3)

    search_input = driver.find_element(By.XPATH, '//input[@name="search"]')
    search_input.send_keys(product_name + Keys.ENTER)
    time.sleep(3)

    suggestions = []

    try:
        # Find all product elements in the search results
        product_elements = driver.find_elements(By.CLASS_NAME, 'goods-tile__inner')

        for product in product_elements:
            try:
                # Get product name
                product_name = product.find_element(By.CLASS_NAME, 'goods-tile__title').text.strip()

                # Get product link
                product_link = product.find_element(By.CLASS_NAME, 'goods-tile__heading').get_attribute('href')

                # Get product price
                try:
                    product_price = product.find_element(By.CLASS_NAME, 'goods-tile__price-value').text.strip()
                except NoSuchElementException:
                    product_price = "Price not available"

                # Get product image URL using the provided XPath
                try:
                    product_image = product.find_element(By.XPATH, './/a[contains(@class,"goods-tile__picture")]/img[1]').get_attribute('src')
                except NoSuchElementException:
                    product_image = None  # Set to None if image is not found

                suggestions.append({
                    'name': product_name,
                    'url': product_link,
                    'price': product_price,
                    'image': product_image  # Add image URL to the suggestion
                })

            except NoSuchElementException:
                logger.error("Error extracting product details for a suggestion, skipping.")
                continue

    finally:
        # driver.quit()
        quit_driver()

    logger.info(f"Found {len(suggestions)} suggestions for '{product_name}'.")
    return suggestions


def scrape_rozetka_product(product_name):
    driver = get_driver()

    # search_url = f"https://rozetka.com.ua/search/?text={product_name.replace(' ', '%20')}"
    # driver.get(search_url)

    driver.get('https://rozetka.com.ua/search/')
    time.sleep(3)

    search_input = driver.find_element(By.XPATH, '//input[@name="search"]')
    search_input.send_keys(product_name + Keys.ENTER)
    time.sleep(3)

    try:
        current_url = driver.current_url

        if 'search' in current_url:
            product_link = current_url
            logger.info(f"Already on product page: {product_link}")
        else:
            product_link = driver.find_element(By.CLASS_NAME, 'goods-tile__heading').get_attribute('href')
            logger.info(f"Found product link: {product_link}")

        product_details = scrape_rozetka_product_details(driver, product_link)

    finally:
        # driver.quit()
        quit_driver()

    return product_details


def scrape_rozetka_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)

    product_name = driver.find_element(By.TAG_NAME, 'h1').text.strip()
    product_price = driver.find_element(By.CLASS_NAME, 'product-price__big').text.strip()

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
            logger.warn("No rating found for this review, skipping.")
            continue

    logger.info(f"Scraped {len(reviews)} valid reviews with ratings.")
    return reviews

