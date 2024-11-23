from django.urls import path, include
from . import views
from .views import mark_review_for_review, list_reviews_needing_review, update_review_sentiment, add_user_review, \
    list_ml_models, activate_ml_model, train_model, get_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

admin_patterns = [
    path('reviews/', list_reviews_needing_review, name='list_reviews_needing_review'),
    path('reviews/<int:review_id>/update-sentiment/', update_review_sentiment, name='update_review_sentiment'),
    path('models/', list_ml_models, name='list-ml-models'),
    path('models/<int:model_id>/activate/', activate_ml_model, name='activate-ml-model'),
    path('models/train/', train_model, name='train-model'),
]

urlpatterns = [
    path('suggestions/', views.get_product_suggestions, name='product-suggestions'),
    path('product/', views.get_product_details, name='product-details'),
    path('product/<int:product_id>/reviews/', views.get_reviews_for_product, name='product-reviews'),
    path('categories/', views.get_rozetka_categories, name='product-categories'),
    path('reviews/<int:review_id>/mark-for-review/', mark_review_for_review, name='mark_review_for_review'),
    path('product/<int:product_id>/add-review/', add_user_review, name='add_user_review'),
    path('admin/', include(admin_patterns)),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', get_user, name='get_user'),
]
