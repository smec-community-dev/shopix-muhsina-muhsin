from django.urls import path
from seller import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sellerhome/', views.seller_home_view, name='sellerhome'),
    path('addproduct/', views.addproduct, name = "addproduct"),
    path("product_detail/<int:pk>/", views.product_detail, name="product_detail"),
    path('sellerprofile/', views.sellerprofile, name = "sellerprofile"),
    path("product/edit/<slug:slug>/", views.edit_product, name="edit_product"),
    path('logout/', views.seller_logout, name='logout'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
]
