
from django.urls import path
from .import views
urlpatterns = [
    path('profile/',views.profile_view,name='profile'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('cart/',views.cart_view,name='cart'),
    path('add_to_cart/<uuid:variant_id>/', views.add_cart, name='add_to_cart'),
    path('update_quantity/<uuid:item_id>/<str:action>/', views.cart_update_quantity, name='update_quantity'),
    path('remove_item/<uuid:item_id>/', views.cart_remove_item, name='remove_item'),
    # path('singleview/<uuid:id>/', views.single_view, name='singleview'),
    path('product/<uuid:id>/', views.variant_page, name='variant_page'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<uuid:variant_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/remove/<uuid:wishlist_item_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('wishlist/clear/',views.clear_wishlist,name='clear_wishlist'),
]
