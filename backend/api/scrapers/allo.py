from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from ..utils.web_driver import get_driver  # Import the centralized get_driver function


def scrape_allo_product(product_name):
    driver = get_driver()

    # URL for searching the product on Allo
    search_url = f"https://allo.ua/ua/catalogsearch/result/?q={product_name.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(3)

    try:
        # Find the first product link in the search results (Allo uses 'product-card__title' class)
        product_link = driver.find_element(By.CLASS_NAME, 'product-card__title').get_attribute('href')
        print(f"Found product link: {product_link}")

        # Scrape the product details
        product_details = scrape_allo_product_details(driver, product_link)

    finally:
        driver.quit()

    return product_details


def scrape_allo_product_details(driver, product_url):
    driver.get(product_url)
    time.sleep(3)

    # Extract product name and price
    product_name = driver.find_element(By.TAG_NAME, 'h1').text.strip()
    product_price = driver.find_element(By.CSS_SELECTOR, '.p-trade-price__current>span').text.strip()

    # print(f"Scraped product: {product_name}, Price: {product_price}")

    # Allo might have reviews; scrape them if available
    reviews = scrape_allo_reviews(driver, product_url)

    return {
        'name': product_name,
        'price': product_price,
        'url': product_url,
        'reviews': reviews
    }


def scrape_allo_reviews(driver, product_url):
    # Allo may have a reviews section; you can modify this to match the actual HTML structure
    reviews = []

    try:
        review_elements = driver.find_elements(By.XPATH, '//div[@itemprop="review"]')
        for review_element in review_elements:
            review_text = review_element.find_element(By.CSS_SELECTOR, '.product-comment .product-comment__text .text').text.strip()

            # Attempt to get the rating
            try:
                review_rating_element = review_element.find_element(By.CLASS_NAME, 'user__rating--estimate')
                review_rating = float(review_rating_element.text.strip())
            except NoSuchElementException:
                review_rating = None  # If rating is not found, set to None

            reviews.append({
                'text': review_text,
                'rating': review_rating
            })

        print(f"Scraped {len(reviews)} reviews.")

    except NoSuchElementException:
        print("No reviews found for this product.")

    return reviews

