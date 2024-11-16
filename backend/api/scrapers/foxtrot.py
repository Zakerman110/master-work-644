from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from backend.logger import logger
from ..utils.web_driver import get_driver, quit_driver  # Import the centralized get_driver function

def scrape_foxtrot_product(product_name):
    driver = get_driver()

    # Construct the search URL for Foxtrot
    # search_url = f"https://www.foxtrot.com.ua/uk/search?query={product_name.replace(' ', '%20')}"
    # driver.get(search_url)
    # time.sleep(3)  # Allow some time for the page to load

    driver.get('https://comfy.ua/')
    time.sleep(3)

    search_input = driver.find_element(By.XPATH, '//input[@type="search"]')
    search_input.send_keys(product_name + Keys.ENTER)
    time.sleep(3)

    try:
        # Find the first product link in the search results
        product_link_element = driver.find_element(By.CLASS_NAME, 'card__title')
        product_link = product_link_element.get_attribute('href')
        logger.info(f"Found product link: {product_link}")

        # Scrape the product details
        product_details = scrape_foxtrot_product_details(driver, product_link)

    finally:
        quit_driver()

    return product_details


def scrape_foxtrot_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)  # Allow time for the product page to load

    # Extract product name
    product_name_element = driver.find_element(By.XPATH, '//h1[@id="product-page-title"]')
    product_name = product_name_element.text.strip() if product_name_element else "N/A"

    # Extract product price
    product_price_element = driver.find_element(By.XPATH, '//div[@class="product-box__main_price"]')
    product_price = product_price_element.text.strip() if product_price_element else "N/A"

    # print(f"Scraped product: {product_name}, Price: {product_price}")

    # Extract reviews (if available)
    reviews = scrape_foxtrot_reviews(driver)

    return {
        'name': product_name,
        'price': product_price,
        'url': product_url,
        'reviews': reviews
    }


def scrape_foxtrot_reviews(driver):
    reviews = []

    try:
        # Scroll to the reviews section to ensure it's in view
        review_section = driver.find_element(By.CLASS_NAME, 'comments-container')  # Update this if needed
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", review_section)
        time.sleep(2)  # Wait for reviews to load

        # Find individual review elements
        review_elements = driver.find_elements(By.XPATH, '//div[@class="product-comment__item"]')  # Update with actual class

        for review_element in review_elements:
            # Extract review text
            review_text_element = review_element.find_element(By.CLASS_NAME, 'product-comment__item-text')
            review_text = review_text_element.text.strip() if review_text_element else "No review text"

            # Extract review rating
            try:
                rating_element = review_element.find_element(By.CLASS_NAME, 'product-comment__item-rating-num')
                rating_text = rating_element.text.strip()
                review_rating = float(rating_text.split('/')[0])
            except NoSuchElementException:
                review_rating = None  # If rating is missing

            reviews.append({
                'text': review_text,
                'rating': review_rating
            })

        logger.info(f"Scraped {len(reviews)} reviews.")

    except NoSuchElementException:
        logger.warn("No reviews section found for this product.")

    return reviews
