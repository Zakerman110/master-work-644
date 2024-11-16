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
    source, _ = ProductSource.objects.update_or_create(
        product=product,
        marketplace=product_data['marketplace'],  # Marketplace name e.g., 'rozetka'
        defaults={
            'url': product_data['url'],
            'price': product_data['price'],
            'last_updated': datetime.now(),
        }
    )

    # Step 3: Add reviews for this ProductSource entry
    # Ensure that existing reviews for this source are not duplicated
    existing_reviews = set(
        source.reviews.values_list('text', flat=True)
    )  # Use 'text' as a unique identifier for simplicity (can be enhanced)

    new_reviews = [
        Review(
            product_source=source,
            text=review['text'],
            rating=review['rating']
        )
        for review in product_data.get('reviews', [])
        if review['text'] not in existing_reviews  # Avoid duplicates
    ]

    if new_reviews:
        Review.objects.bulk_create(new_reviews)
        logger.info(f"Added {len(new_reviews)} new reviews for product '{product.name}' on {source.marketplace}.")
    else:
        logger.info(f"No new reviews to add for product '{product.name}' on {source.marketplace}.")

    logger.info(f"Data for '{product.name}' on '{source.marketplace}' has been saved to the database.")
