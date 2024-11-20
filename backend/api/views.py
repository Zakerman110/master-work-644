from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.scrapers import scraper_manager
from api.models import Product, Review, ProductSource
from api.serializers import ProductSerializer, DetailedProductSerializer, ReviewSerializer
from api.utils.category_utils import ROZETKA_CATEGORIES
from api.sentiment.sentiment_model import predict_sentiment


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

    paginator = PageNumberPagination()
    paginator.page_size = 21
    paginated_suggestions = paginator.paginate_queryset(suggestions, request)

    # Serialize paginated suggestions
    serialized_suggestions = ProductSerializer(paginated_suggestions, many=True)

    # Return paginated response
    return paginator.get_paginated_response(serialized_suggestions.data)


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
    Retrieve all reviews for a product, grouped by its sources, with sentiment analysis.
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


@api_view(['POST'])
def mark_review_for_review(request, review_id):
    """
    Mark a review for admin review.
    """
    try:
        review = Review.objects.get(id=review_id)
        review.needs_review = True
        review.save()
        return Response({"message": "Review marked for admin review."})
    except Review.DoesNotExist:
        return Response({"error": "Review not found."}, status=404)


@api_view(['GET'])
def list_reviews_needing_review(request):
    """
    List reviews marked for admin review.
    """
    reviews = Review.objects.filter(needs_review=True)
    paginator = PageNumberPagination()
    paginated_reviews = paginator.paginate_queryset(reviews, request)
    serialized_reviews = ReviewSerializer(paginated_reviews, many=True)
    return paginator.get_paginated_response(serialized_reviews.data)


@api_view(['POST'])
def update_review_sentiment(request, review_id):
    """
    Update the sentiment of a review by an admin.
    """
    try:
        review = Review.objects.get(id=review_id)
        new_sentiment = request.data.get("human_sentiment")
        if not new_sentiment:
            return Response({"error": "Human sentiment is required."}, status=400)

        review.human_sentiment = new_sentiment
        review.needs_review = False
        review.save()

        return Response({"message": "Review sentiment updated successfully."})
    except Review.DoesNotExist:
        return Response({"error": "Review not found."}, status=404)


@api_view(['POST'])
def add_user_review(request, product_id):
    """
    Add a user-generated review for a specific product.
    """
    try:
        product = Product.objects.get(id=product_id)
        data = request.data

        # Create a ProductSource for user-generated reviews if it doesn't exist
        source, created = ProductSource.objects.get_or_create(
            product=product,
            marketplace="self",  # Indicating that this is user-generated
            defaults={
                'url': '',  # Not applicable for user-generated reviews
                'price': None,  # Not applicable
            },
        )

        # Add the user review
        Review.objects.create(
            product_source=source,
            text=data.get('text'),
            rating=data.get('rating'),
            model_sentiment=predict_sentiment(data.get('text'))
        )

        return Response({"message": "Review added successfully!"}, status=status.HTTP_201_CREATED)

    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

