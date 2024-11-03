from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.scrapers import scraper_manager


@api_view(['GET'])
def hello_world(request):
    product_details = scraper_manager.scrape_and_save_product("iPhone 12 128GB Purpl", "citrus")
    return Response(product_details)
