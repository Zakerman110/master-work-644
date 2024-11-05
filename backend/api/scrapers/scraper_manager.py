from concurrent.futures import ThreadPoolExecutor, as_completed
from api.models import Product
from api.scrapers.comfy import scrape_comfy_product
from api.scrapers.rozetka import scrape_rozetka_product
from api.scrapers.allo import scrape_allo_product
from api.scrapers.foxtrot import scrape_foxtrot_product
from api.scrapers.citrus import scrape_citrus_product
from api.utils.db_utils import save_product_to_db

def scrape_and_save_product(product_name):
    """
    Check if the product already exists in the database by name.
    If found, return the product.
    If not, scrape the product concurrently across multiple sources and save it to the database.
    """

    products = Product.objects.filter(name__icontains=product_name)

    if products.exists():
        product = products.first()
        print(f"Product '{product_name}' found in the database.")
        return product

    print(f"Product '{product_name}' not found in the database. Scraping now...")

    scrape_functions = {
        'rozetka': scrape_rozetka_product,
        'comfy': scrape_comfy_product,
        'allo': scrape_allo_product,
        'foxtrot': scrape_foxtrot_product,
        'citrus': scrape_citrus_product,
    }

    scraped_data = []
    with ThreadPoolExecutor() as executor:
        future_to_source = {
            executor.submit(scrape_func, product_name): source
            for source, scrape_func in scrape_functions.items()
        }

        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                product_data = future.result()
                if product_data:
                    scraped_data.append(product_data)
                    print(f"Data from {source} has been scraped successfully.")
            except Exception as e:
                print(f"Error scraping {source}: {e}")

    if scraped_data:
        for data in scraped_data:
            save_product_to_db(data)
        print(f"Data for '{product_name}' has been saved to the database.")
        return Product.objects.filter(name__iexact=product_name).first()
    else:
        print(f"No product found for '{product_name}' after scraping.")
        return None
