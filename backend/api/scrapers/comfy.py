from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.utils.search_utils import find_best_match

from backend.logger import logger

from api.utils.web_driver import get_driver, quit_driver
import time


def scrape_comfy_product(product_name, partial_names):
    driver = get_driver()

    try:
        # Base URL for Comfy search
        base_url = 'https://comfy.ua/'

        # Initialize variables to track the best match
        best_match = None
        best_score = 0

        # Iterate through partial names to perform searches
        for partial_name in partial_names:
            logger.info(f"Searching Comfy with query: {partial_name}")

            # Navigate to Comfy's home page
            driver.get(base_url)
            time.sleep(3)  # Allow the page to load

            # Locate the search input and perform the search
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="q"]'))
            )
            search_input.clear()  # Clear the search bar for the next query
            search_input.send_keys(partial_name + Keys.ENTER)
            time.sleep(3)  # Allow search results to load

            try:
                # Wait for the product elements to load
                product_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'prdl-item'))
                )

                # Extract product names and links from the results
                results = []
                for product in product_elements:
                    try:
                        name = product.find_element(By.CLASS_NAME, 'prdl-item__name').text.strip()
                        link = product.find_element(By.CLASS_NAME, 'prdl-item__name').get_attribute('href')
                        results.append({'name': name, 'url': link})
                    except Exception as e:
                        logger.error(f"Error extracting product details: {e}")
                        continue

                # Find the best match for the current search
                match = find_best_match(product_name, results)
                if match and match['score'] > best_score:
                    best_score = match['score']
                    best_match = match

            except Exception as e:
                logger.info(f"No results found for query: {partial_name}")
                continue

        if best_match:
            logger.info(f"Best match found on Comfy: {best_match['name']} with score {best_score}")
            # Navigate to the best match's product page
            product_details = scrape_comfy_product_details(driver, best_match['url'])
            return product_details
        else:
            logger.info("No suitable match found on Comfy.")
            return None

    finally:
        quit_driver()


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
