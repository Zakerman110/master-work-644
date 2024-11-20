from django.urls import path, include
from . import views
from .views import mark_review_for_review, list_reviews_needing_review, update_review_sentiment

admin_patterns = [
    path('reviews/', list_reviews_needing_review, name='list_reviews_needing_review'),
    path('reviews/<int:review_id>/update-sentiment/', update_review_sentiment, name='update_review_sentiment'),
]

urlpatterns = [
    path('suggestions/', views.get_product_suggestions, name='product-suggestions'),
    path('product/', views.get_product_details, name='product-details'),
    path('product/<int:product_id>/reviews/', views.get_reviews_for_product, name='product-reviews'),
    path('categories/', views.get_rozetka_categories, name='product-categories'),
    path('reviews/<int:review_id>/mark-for-review/', mark_review_for_review, name='mark_review_for_review'),
    path('admin/', include(admin_patterns)),
]
