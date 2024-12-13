from django.contrib.auth.models import User
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
            'reviews',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'rating', 'model_sentiment', 'confidence', 'human_sentiment', 'needs_review',]


class DetailedProductSerializer(serializers.ModelSerializer):
    sources = ProductSourceSerializer(many=True, read_only=True)  # Nested ProductSource data
    reviews = ReviewSerializer(many=True, read_only=True, source='sources__reviews')

    class Meta:
        model = Product
        fields = ['id', 'name', 'image_url', 'description', 'is_detailed', 'sources', 'reviews']


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'role']

    def get_role(self, obj):
        return 'admin' if obj.is_staff else 'user'
