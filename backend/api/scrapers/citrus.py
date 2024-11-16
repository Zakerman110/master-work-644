from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from backend.logger import logger
from ..utils.web_driver import get_driver, quit_driver  # Import the centralized get_driver function


def scrape_citrus_product(product_name):
    driver = get_driver()

    # Construct the search URL for Citrus
    search_url = f"https://www.ctrs.com.ua/ru/search/?query={product_name.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(3)  # Allow some time for the page to load

    try:
        # Check if the empty result section is present
        wait = WebDriverWait(driver, 10)  # Set a maximum wait time of 10 seconds
        try:
            empty_section = wait.until(
                EC.presence_of_element_located((By.XPATH, '//section[contains(@class,"EmptySearch_emptyContainer")]'))
            )
            if empty_section:
                logger.info("No results found for the given product. Skipping scraping.")
                quit_driver()  # Quit the driver
                return None  # Skip scraping and return None
        except Exception as e:
            logger.info("No empty result section detected. Proceeding with scraping.")

        # Find the first product link in the search results
        product_link_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="catalog-facet"]//a[contains(@class,"MainProductCard-module__link")]'))
        )
        product_link = product_link_element.get_attribute('href')
        logger.info(f"Found product link: {product_link}")

        # Scrape the product details
        product_details = scrape_citrus_product_details(driver, product_link)

    except Exception as e:
        logger.error(f"An error occurred while scraping Citrus: {e}")
        product_details = None

    finally:
        quit_driver()  # Ensure the driver quits

    return product_details


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
