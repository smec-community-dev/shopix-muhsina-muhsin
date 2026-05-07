
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('login/',views.login_view,name='login'),
    path('buyerregister/',views.customer_register,name='buyerregister'),
    path('sellerregister/', views.seller_register,name='sellerregister'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/',views.logout_view,name='logout'),
    path('',views.home_view,name='home'),
    path('product/<int:id>/', views.single_variant_view, name='single_fetch'),
    path('core_product/', views.core_product, name='core_product'),
    path('products/', views.core_product, name='products'),
    path('contactus/', views.contactus, name='contactus'),
    path('privacy-policy/', views.privacypolicy, name='privacypolicy'),
    path('terms-of-service/', views.termsofservice, name='termsofservice'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('search/', views.search_view, name='search'),

]
