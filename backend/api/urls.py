from django.urls import path
from . import views

urlpatterns = [
    path('suggestions/', views.get_product_suggestions, name='product-suggestions'),
    path('product/', views.get_product_details, name='product-details'),
]
