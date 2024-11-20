from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_detailed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductSource(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sources')
    marketplace = models.CharField(max_length=50)  # e.g., 'rozetka', 'comfy'
    url = models.URLField()
    price = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.marketplace} - {self.product.name}"


class Review(models.Model):
    product_source = models.ForeignKey(ProductSource, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    sentiment = models.TextField()
    rating = models.FloatField()

    def __str__(self):
        return f"Review for {self.product_source.product.name} on {self.product_source.marketplace}"
