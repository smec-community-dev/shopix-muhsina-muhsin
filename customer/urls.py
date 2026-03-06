from django.urls import path
from .import views
urlpatterns = [
    path('profile/',views.profile_view,name='profile'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('cart/',views.cart_view,name='cart'),
    path('add_to_cart/<int:variant_id>/', views.add_cart, name='add_to_cart'),
    path('update_quantity/<int:item_id>/<str:action>/', views.cart_update_quantity, name='update_quantity'),
    path('remove_item/<int:item_id>/', views.cart_remove_item, name='remove_item')
]
