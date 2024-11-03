from api.models import Product, Review


def save_product_to_db(product_data):
    """
    Save a product and its reviews to the database if it doesn't already exist.
    If the product exists, update its price and updated_at timestamp.
    """
    # Check if the product already exists by URL
    product, created = Product.objects.get_or_create(
        url=product_data['url'],
        defaults={
            'name': product_data['name'],
            'price': product_data['price'],
        }
    )

    if created:
        print(f"Product '{product_data['name']}' added to the database.")
    else:
        # If the product exists, check if we need to update it
        if product.price != product_data['price']:
            product.price = product_data['price']
            product.save()  # This will also update the `updated_at` field
            print(f"Product '{product_data['name']}' updated with new price.")
        else:
            print(f"Product '{product_data['name']}' already exists and is up-to-date.")

    if created:
        for review in product_data['reviews']:
            Review.objects.create(
                product=product,
                text=review['text'],
                rating=review['rating']
            )
        print(f"Added {len(product_data['reviews'])} reviews for product '{product_data['name']}'.")
