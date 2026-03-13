from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from customer.models import *

from seller.models import Product, SellerProfile, ProductVariant

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            if user.role == 'SELLER':
                return redirect('sellerhome')

            elif user.role == 'CUSTOMER':
                return redirect('home')

            elif user.role == 'ADMIN':
                return redirect('admin_dashboard')

        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'core_templates/loginpage.html')


def customer_register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'core_templates/customer_register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'core_templates/customer_register.html')

        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'core_templates/customer_register.html')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone
            )

            messages.success(request, 'Customer registration successful.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error: {e}')
            return render(request, 'core_templates/customer_register.html')

    return render(request, 'core_templates/customer_register.html')

def seller_register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'core_templates/seller_register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'core_templates/seller_register.html')

        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'core_templates/seller_register.html')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone,
                role='SELLER' 
            )

            SellerProfile.objects.create(user=user)

            messages.success(request, 'Seller registration successful. You can now log in.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Error: {e}')
            return render(request, 'core_templates/seller_register.html')

    return render(request, 'core_templates/seller_register.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def home_view(request):
    products = ProductVariant.objects.all()
    user_wishlist_ids = [] # Default to empty for guests

    if request.user.is_authenticated:
        # We look through WishlistItem, filtering by the user linked to the Wishlist
        user_wishlist_ids = WishlistItem.objects.filter(
            wishlist__user=request.user
        ).values_list('variant_id', flat=True)

    context = {
        'products': products,
        'user_wishlist_ids': list(user_wishlist_ids), # Pass IDs to the template
    }
    
    return render(request, 'core_templates/homepage.html', context)


def single_variant_view(request, id):
    """Render HTML for a single product variant."""
    variant = get_object_or_404(
        ProductVariant.objects.select_related('product__seller', 'product__subcategory')
                              .prefetch_related('product__images', 'images'),
        id=id
    )
    context = {
        'variant': variant,
    }
    return render(request, 'customer_templates/single_fetch.html', context)
