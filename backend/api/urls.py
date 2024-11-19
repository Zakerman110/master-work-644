from django.urls import path
from . import views

urlpatterns = [
    path('suggestions/', views.get_product_suggestions, name='product-suggestions'),
    path('product/', views.get_product_details, name='product-details'),
    path('product/<int:product_id>/reviews/', views.get_reviews_for_product, name='product-reviews'),
    path('categories/', views.get_rozetka_categories, name='product-categories'),
]
