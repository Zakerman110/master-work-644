from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.scrapers import scraper_manager
from api.models import Product
from api.serializers import ProductSerializer, DetailedProductSerializer, ReviewSerializer
from api.utils.category_utils import ROZETKA_CATEGORIES


@api_view(['GET'])
def get_product_suggestions(request):
    """
    Retrieve product suggestions based on a search query.
    """
    query = request.GET.get('query', '')
    category_id = request.GET.get('category_id', None)
    if not query:
        return Response({"error": "Query parameter is required."}, status=400)

    # Get product suggestions from scraper_manager
    suggestions = scraper_manager.get_product_suggestions(query, category_id)

    # Serialize suggestions
    serialized_suggestions = ProductSerializer(suggestions, many=True)
    return Response(serialized_suggestions.data)


@api_view(['GET'])
def get_product_details(request):
    """
    Retrieve detailed information and reviews for a specific product by name.
    """
    product_name = request.GET.get('name', '')
    if not product_name:
        return Response({"error": "Name parameter is required."}, status=400)

    # Get or scrape detailed product information
    product = scraper_manager.scrape_and_save_product(product_name)

    if not product:
        return Response({"error": "Product not found."}, status=404)

    # Serialize detailed product
    serialized_product = DetailedProductSerializer(product)
    return Response(serialized_product.data)

@api_view(['GET'])
def get_reviews_for_product(request, product_id):
    """
    Retrieve all reviews for a product, grouped by its sources.
    """
    try:
        product = Product.objects.get(id=product_id)
        sources = product.sources.all()

        reviews_data = []
        for source in sources:
            reviews = source.reviews.all()
            serialized_reviews = ReviewSerializer(reviews, many=True).data
            reviews_data.append({
                "marketplace": source.marketplace,
                "reviews": serialized_reviews
            })

        return Response(reviews_data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=404)


@api_view(['GET'])
def get_rozetka_categories(request):
    """
    Return a list of available Rozetka categories.
    """
    categories = [{"name": name, "id": id} for name, id in ROZETKA_CATEGORIES.items()]
    return Response(categories)

