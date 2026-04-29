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
    path('categorymanagement/', views.categorymanagement, name='categorymanagement'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<uuid:pk>/', views.edit_category, name='edit_category'),
    path('category/delete/<uuid:pk>/', views.delete_category, name='delete_category'),
    path('sub-categories/', views.subcategory_list, name='subcategorymanagement'),
    path('sub-categories/add/', views.add_subcategory, name='add_subcategory'),
    path('sub-categories/edit/<uuid:pk>/', views.edit_subcategory, name='edit_subcategory'),
    path('sub-categories/delete/<uuid:pk>/', views.delete_subcategory, name='delete_subcategory'),
]