from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from django.db.models import Q
from api.models import Product, ProductSource
from api.scrapers.comfy import scrape_comfy_product
from api.scrapers.rozetka import scrape_rozetka_product, scrape_rozetka_suggestions
from api.scrapers.allo import scrape_allo_product
from api.scrapers.foxtrot import scrape_foxtrot_product
from api.scrapers.citrus import scrape_citrus_product
from api.utils.category_utils import ROZETKA_CATEGORIES
from api.utils.db_utils import save_product_to_db
from api.utils.search_utils import generate_partial_product_names
from backend.logger import logger
from urllib.parse import urlparse


def get_product_suggestions(product_name, category_id=None):
    """
    Retrieve product suggestions based on the product name.
    First, try to find matching products in the database.
    If no products are found, scrape new suggestions from Rozetka.
    """
    if category_id and category_id.strip():
        category_name = next((k for k, v in ROZETKA_CATEGORIES.items() if v == int(category_id)), None)
    else:
        category_name = None

    logger.info(f"Fetching product suggestions for '{product_name}', category '{category_name}'")

    filters = Q(name__icontains=product_name)
    if category_name:
        filters &= Q(category__icontains=category_name)

    suggestions = Product.objects.filter(filters)

    if suggestions.exists():
        logger.info(f"Found existing suggestions for '{product_name}' in the database.")
        return suggestions

    logger.info(f"No matching products found for '{product_name}' in the database. Scraping suggestions...")

    # Primary source for product suggestions (e.g., Rozetka)
    suggestions_data = scrape_rozetka_suggestions(product_name, category_id)

    # Save each suggestion to the database if it doesn't already exist
    for suggestion in suggestions_data:
        # Find or create the main Product entry
        product, _ = Product.objects.get_or_create(
            name=suggestion['name'],
            category=suggestion['category'],
            defaults={
                'image_url': suggestion.get('image', ''),
                'is_detailed': False,  # Mark as non-detailed initially
            }
        )

        # Create or update the ProductSource for this suggestion
        ProductSource.objects.update_or_create(
            product=product,
            marketplace='rozetka',  # Assuming 'rozetka' is the marketplace for suggestions
            url=suggestion['url'],
            defaults={
                'price': suggestion.get('price', ''),
                'last_updated': datetime.now()
            }
        )

    logger.info(f"Scraped and saved suggestions for '{product_name}', category '{category_name}'.")
    return Product.objects.filter(filters)


def scrape_and_save_product(product_name):
    """
    Check if the consolidated product already exists by name.
    If not, scrape data from multiple sources and create a consolidated product.
    Returns the consolidated product with data from all sources.
    """
    logger.info(f"Scraping detailed product data for '{product_name}'")
    # Find or create the consolidated product entry
    product, created = Product.objects.get_or_create(name__iexact=product_name, defaults={'name': product_name})

    if not created and product.is_detailed:
        logger.info(f"Product '{product_name}' is already detailed in the database.")
        return product

    logger.info(f"Scraping product data for '{product_name}' from multiple sources...")

    # name from url:
    # identifier = get_identifier_from_product_source(product)
    # # TODO: Add check, if identifier consists only of digits, that use original product_name
    # if identifier is not None and not identifier.isdigit():
    #     product_name = identifier
    partial_names = generate_partial_product_names(product_name)

    # Scrape functions for each marketplace
    scrape_functions = {
        'rozetka': scrape_rozetka_product,
        # 'comfy': scrape_comfy_product,
        # 'allo': scrape_allo_product,
        # 'foxtrot': scrape_foxtrot_product,
        'citrus': scrape_citrus_product,
    }

    # Concurrently scrape each marketplace for the product data
    with ThreadPoolExecutor() as executor:
        future_to_source = {
            executor.submit(scrape_func, product_name, partial_names): source
            for source, scrape_func in scrape_functions.items()
        }

        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                product_data = future.result()
                if product_data:
                    product_data['marketplace'] = source  # Tag data with the marketplace source
                    save_product_to_db(product_data, product_id=product.id)  # Pass product_id for linking
                    logger.info(f"Data from {source} has been saved successfully.")
            except Exception as e:
                logger.error(f"Error scraping {source}: {e}")

    # Mark the product as detailed if data from at least one source was saved
    if ProductSource.objects.filter(product=product).exists():
        product.is_detailed = True
        product.save()
        logger.info(f"Product '{product_name}' marked as detailed.")

    return product
