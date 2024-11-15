from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.scrapers import scraper_manager
from api.models import Product
from api.serializers import ProductSerializer, DetailedProductSerializer


@api_view(['GET'])
def get_product_suggestions(request):
    """
    Retrieve product suggestions based on a search query.
    """
    query = request.GET.get('query', '')
    if not query:
        return Response({"error": "Query parameter is required."}, status=400)

    # Get product suggestions from scraper_manager
    suggestions = scraper_manager.get_product_suggestions(query)

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
