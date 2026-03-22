from django.urls import path
from . import views

urlpatterns = [
    path('sellerhome/', views.seller_home_view, name='sellerhome'),

    path('addproduct/', views.addproduct, name='addproduct'),  # cleaner URL
    path('products/', views.productlist, name='productlist'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/edit/<slug:slug>/', views.edit_product, name='edit_product'),

    path('profile/', views.sellerprofile, name='sellerprofile'),
    path('profile/edit/', views.edit_seller_profile, name='edit_profile'),

    path('orders/', views.order_view, name='orderview'),

    path('logout/', views.seller_logout, name='logout'),
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
]