from django.urls import path
from . import views

urlpatterns = [
    path('price/<int:price_id>/', views.product_price_redirect_view, name='product-price-redirect'),
    path('start/', views.checkout_redirect_view, name='stripe-checkout-start'),
    path('success/', views.checkout_finalize_view, name='stripe-checkout-end'),
]
