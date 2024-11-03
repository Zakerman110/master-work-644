from api.models import Product
from api.scrapers.comfy import scrape_comfy_product
from api.scrapers.rozetka import scrape_rozetka_product
from api.scrapers.allo import scrape_allo_product
from api.scrapers.foxtrot import scrape_foxtrot_product
from api.scrapers.citrus import scrape_citrus_product
from api.utils.db_utils import save_product_to_db
from api.utils.web_driver import get_driver


def scrape_and_save_product(product_name, source='rozetka'):
    """
    First check if the product already exists in the database by name.
    If found, return the product.
    If not, scrape the product and save it to the database.
    """
    # Check if the product exists in the database by name
    products = Product.objects.filter(name__icontains=product_name)

    if products.exists():
        product = products.first()  # Get the first matching product
        print(f"Product '{product_name}' found in the database.")
        return product

    else:
        print(f"Product '{product_name}' not found in the database. Scraping now...")

        driver = get_driver()
        if source == 'rozetka':
            product_data = scrape_rozetka_product(product_name)
        elif source == 'comfy':
            product_data = scrape_comfy_product(product_name)
        elif source == 'allo':
            product_data = scrape_allo_product(product_name)
        elif source == 'foxtrot':
            product_data = scrape_foxtrot_product(product_name)
        elif source == 'citrus':
            product_data = scrape_citrus_product(product_name)
        else:
            raise ValueError(f"Source '{source}' is not supported.")
        driver.quit()

        if product_data:
            save_product_to_db(product_data)

            product = Product.objects.filter(name__iexact=product_name).first()
            return product

        else:
            print(f"No product found for '{product_name}' after scraping.")
            return None