from django.urls import path
from admin_app import views

urlpatterns = [
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('customerlisting/', views.customerlisting, name='customerlisting'),
    path('productlisting/', views.productlisting, name='productlisting'),
    path('sellerlisting/', views.sellerlisting, name='sellerlisting'),
    path('sellerdetails/<uuid:user_id>/', views.seller_detail, name='sellerdetails'),
    path('approveseller/<uuid:user_id>/approve/', views.approve_seller, name='approveseller'),
    path('rejectseller/<uuid:user_id>/reject/', views.reject_seller, name='rejectseller'),
    path('seller/<uuid:user_id>/', views.seller_detail, name='seller_detail'),
    path('adminsettings/', views.adminsettings, name='adminsettings'),
]