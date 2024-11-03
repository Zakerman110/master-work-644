from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.FloatField()

    def __str__(self):
        return f"Review for {self.product.name}: {self.rating} stars"
