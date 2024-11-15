from api.models import Product, ProductSource, Review
from datetime import datetime
from backend.logger import logger


def save_product_to_db(product_data, product_id):
    """
    Save a product and its marketplace-specific data (price, URL, and reviews) to the database.
    Updates existing entries if they already exist.
    """
    # Retrieve the main Product entry using product_id
    product = Product.objects.get(id=product_id)

    # Step 2: Save or update the ProductSource entry for this marketplace
    source, created = ProductSource.objects.update_or_create(
        product=product,
        marketplace=product_data['marketplace'],  # Marketplace name e.g., 'rozetka'
        defaults={
            'url': product_data['url'],
            'price': product_data['price'],
            'last_updated': datetime.now(),
        }
    )

    # Step 3: Save reviews for this ProductSource entry
    if created:  # Only add reviews if this source is new to avoid duplicates
        for review in product_data.get('reviews', []):
            Review.objects.create(
                product_source=source,
                text=review['text'],
                rating=review['rating']
            )
        logger.info(f"Added {len(product_data.get('reviews', []))} reviews for product '{product.name}' on {source.marketplace}.")

    logger.info(f"Data for '{product.name}' on '{source.marketplace}' has been saved to the database.")
