from rest_framework import serializers
from api.models import Product, ProductSource, Review, MLModel


class ProductSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSource
        fields = ['marketplace', 'url', 'price', 'last_updated']


class ProductSerializer(serializers.ModelSerializer):
    sources = ProductSourceSerializer(many=True, read_only=True)  # Nested ProductSource data

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'image_url', 'is_detailed', 'sources']


class MLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = [
            "id",
            "file_name",
            "created_at",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "is_active",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'rating', 'model_sentiment', 'confidence', 'human_sentiment', 'needs_review', "linked_ml_model",]


class DetailedProductSerializer(serializers.ModelSerializer):
    sources = ProductSourceSerializer(many=True, read_only=True)  # Nested ProductSource data
    reviews = ReviewSerializer(many=True, read_only=True, source='sources__reviews')

    class Meta:
        model = Product
        fields = ['id', 'name', 'image_url', 'description', 'is_detailed', 'sources', 'reviews']
