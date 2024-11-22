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
    rating = models.FloatField()
    model_sentiment = models.CharField(max_length=50, default="Neutral")  # Predicted sentiment
    confidence = models.FloatField()
    human_sentiment = models.CharField(max_length=50, null=True, blank=True)  # Corrected sentiment
    needs_review = models.BooleanField(default=False)  # Mark for admin review

    def __str__(self):
        return f"Review for {self.product_source.product.name} on {self.product_source.marketplace}"


class MLModel(models.Model):
    file_name = models.CharField(max_length=255, unique=True)  # The filename of the saved model
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the model was created
    accuracy = models.FloatField(null=True, blank=True)  # Accuracy metric
    precision = models.FloatField(null=True, blank=True)  # Precision metric
    recall = models.FloatField(null=True, blank=True)  # Recall metric
    f1_score = models.FloatField(null=True, blank=True)  # F1-score metric
    is_active = models.BooleanField(default=False)  # Whether this model is currently in use
    reviews = models.ManyToManyField(Review, related_name="models")  # Many-to-Many relationship

    def __str__(self):
        return f"Model {self.file_name} - {'Active' if self.is_active else 'Inactive'}"
