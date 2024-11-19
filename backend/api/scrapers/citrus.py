from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from backend.logger import logger
from ..utils.search_utils import find_best_match
from ..utils.web_driver import get_driver, quit_driver  # Import the centralized get_driver function


def scrape_citrus_product(product_name, partial_names):
    driver = get_driver()

    try:
        # Base URL for Citrus search
        base_url = "https://www.ctrs.com.ua/ru/search/?query={query}"

        # Initialize variables to track the best match
        best_match = None
        best_score = 0

        # Iterate through partial names to perform searches
        for partial_name in partial_names:
            logger.info(f"Searching Citrus with query: {partial_name}")

            # Navigate to the search page
            search_url = base_url.format(query=partial_name.replace(" ", "%20"))
            driver.get(search_url)
            time.sleep(3)  # Allow search results to load

            # Check if the empty result section is present
            try:
                empty_section = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//section[contains(@class,"EmptySearch_emptyContainer")]'))
                )
                if empty_section:
                    logger.info(f"No results found for query: {partial_name}")
                    continue  # Skip to the next partial name
            except:
                logger.info(f"Results found for query: {partial_name}")

            try:
                # TODO: Handle the case, when product is opened directly because of accurate search query
                # Wait for product elements to load
                product_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@class="catalog-facet"]//a[contains(@class,"MainProductCard-module__link")]'))
                )

                # Extract product names and links from the results
                results = []
                for product in product_elements:
                    try:
                        name = product.get_attribute('title').strip()  # Citrus includes titles in the 'title' attribute
                        link = product.get_attribute('href')
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
                logger.info(f"No valid products found for query: {partial_name}. Error: {e}")
                continue

        if best_match:
            logger.info(f"Best match found on Citrus: {best_match['name']} with score {best_score}")
            # Navigate to the best match's product page
            product_details = scrape_citrus_product_details(driver, best_match['url'])
            return product_details
        else:
            logger.info("No suitable match found on Citrus.")
            return None

    finally:
        quit_driver()  # Ensure the driver quits


def scrape_citrus_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)  # Allow time for the product page to load

    # Extract product name
    product_name_element = driver.find_element(By.TAG_NAME, 'h1')
    product_name = product_name_element.text.strip() if product_name_element else "N/A"

    # Extract product price
    product_price_element = driver.find_element(By.XPATH, '//div[contains(@class,"Price_price_")]')  # Update this with actual price class name if different
    product_price = product_price_element.text.strip() if product_price_element else "N/A"

    # print(f"Scraped product: {product_name}, Price: {product_price}")

    # Optionally, scrape reviews if available
    reviews = scrape_citrus_reviews(driver)

    return {
        'name': product_name,
        'price': product_price,
        'url': product_url,
        'reviews': reviews
    }


def scrape_citrus_reviews(driver):
    reviews = []

    try:
        # Scroll to the reviews section to ensure it loads
        review_section = driver.find_element(By.ID, 'reviews')
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", review_section)
        time.sleep(2)  # Wait for reviews to load

        # Find individual review elements
        review_elements = driver.find_elements(By.XPATH, '//div[contains(@class,"Reviews_comment")]/div')  # Adjust with actual class name

        for review_element in review_elements:
            # Extract review text
            review_text_element = review_element.find_element(By.XPATH, './/p[./span[text()="Опыт использования"]]')
            review_text = review_text_element.text.strip() if review_text_element else "No review text"

            # Extract review rating
            try:
                star_elements = review_element.find_elements(By.XPATH,
                                                             './/div[contains(@class,"Rating-module")]/span/*[name()="svg"]/*[name()="path"]')

                filled_stars = 0
                for star in star_elements:
                    fill_color = star.get_attribute("fill")
                    if fill_color == "rgb(255, 193, 7)":  # Yellow star color
                        filled_stars += 1

                review_rating = filled_stars
            except NoSuchElementException:
                review_rating = None  # Set to None if the rating element is missing

            reviews.append({
                'text': review_text,
                'rating': review_rating
            })

        logger.info(f"Scraped {len(reviews)} reviews.")

    except NoSuchElementException:
        logger.warn("No reviews section found for this product.")

    return reviews
