from urllib.parse import urlparse
from rapidfuzz import fuzz
from api.models import ProductSource
from backend.logger import logger


def get_identifier_from_product_source(product):
    # Attempt to retrieve the ProductSource for 'rozetka'
    try:
        product_source = product.sources.get(marketplace="rozetka")

        # Parse the URL to extract the identifier
        parsed_url = urlparse(product_source.url)
        path_segments = parsed_url.path.strip('/').split('/')

        # Extract the product identifier if it exists in the path
        product_identifier = path_segments[1] if len(path_segments) > 1 else None
        logger.info("Identifier: " + product_identifier)
        return product_identifier

    except ProductSource.DoesNotExist:
        logger.warn("No ProductSource found for 'rozetka'")
        return None


def generate_partial_product_names(product_name):
    """
    Generate a list of partial product names for searching other marketplaces.
    """
    # Split the product name into meaningful parts
    parts = product_name.split()
    partial_names = [" ".join(parts[:i]) for i in range(len(parts), 1, -1)]
    logger.info(f"Generated partial names: {partial_names}")
    return partial_names


def find_best_match(suggestion_name, search_results):
    """
    Find the product from the search results that most closely matches the suggestion name.
    """
    best_match = None
    best_score = 0

    for result in search_results:
        score = fuzz.ratio(suggestion_name, result["name"])
        if score > best_score:
            best_score = score
            best_match = result

    if best_match:
        best_match["score"] = best_score

    logger.info(f"Best match: {best_match}, Score: {best_score}")
    return best_match
