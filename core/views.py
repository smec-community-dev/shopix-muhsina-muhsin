from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from customer.models import *
from .models import *
from seller.models import Product, SellerProfile, ProductVariant
import random
from django.core.mail import send_mail
from django.conf import settings

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

        otp = str(random.randint(100000, 999999))

        request.session['register_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password': password,
            'role': 'CUSTOMER'
        }
        request.session['otp'] = otp

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return redirect('verify_otp')

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

        otp = str(random.randint(100000, 999999))

        request.session['register_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password': password,
            'role': 'SELLER'
        }

        request.session['otp'] = otp

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, 'OTP sent to your email. Please verify.')
        return redirect('verify_otp')

    return render(request, 'core_templates/seller_register.html')

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        data = request.session.get('register_data')

        if not session_otp or not data:
            messages.error(request, "Session expired. Please register again.")
            return redirect('customer_register')

        if entered_otp == session_otp:

            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone'],
                role=data['role']
            )

            if data['role'] == 'SELLER':
                SellerProfile.objects.create(user=user)

            request.session.flush()

            messages.success(request, "Account created successfully!")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")

    return render(request, 'core_templates/verify_otp.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def home_view(request):
    products = ProductVariant.objects.all()
    user_wishlist_ids = [] 

    if request.user.is_authenticated:
        user_wishlist_ids = WishlistItem.objects.filter(
            wishlist__user=request.user
        ).values_list('variant_id', flat=True)

    context = {
        'products': products,
        'user_wishlist_ids': list(user_wishlist_ids),
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



def products(request):
    """View to display products page with New Arrivals section and All Products section"""
    from django.db.models import Count
    
    # Get filter/sort params
    category_id = request.GET.get('category_id')
    sort = request.GET.get('sort', 'newest')
    
    # Base queryset for all approved/active products
    base_qs = ProductVariant.objects.filter(
        product__approval_status='APPROVED',
        product__is_active=True
    ).select_related('product', 'product__subcategory__category').prefetch_related('images')
    
    # Apply category filter
    if category_id:
        base_qs = base_qs.filter(product__subcategory__category_id=category_id)
    
    # Apply sorting
    if sort == 'price_asc':
        base_qs = base_qs.order_by('selling_price')
    elif sort == 'price_desc':
        base_qs = base_qs.order_by('-selling_price')
    elif sort == 'name_asc':
        base_qs = base_qs.order_by('product__name')
    elif sort == 'name_desc':
        base_qs = base_qs.order_by('-product__name')
    elif sort == 'newest':
        base_qs = base_qs.order_by('-created_at')
    elif sort == 'oldest':
        base_qs = base_qs.order_by('created_at')
    
    all_products = base_qs
    
    # New arrivals (filtered/sorted same way, last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    new_arrivals = all_products.filter(created_at__gte=seven_days_ago)
    
# Categories with product counts for sidebar - ALL active categories
    categories_qs = Category.objects.filter(is_active=True).annotate(
        product_count=Count(
            'subcategories__products',
            filter=Q(subcategories__products__approval_status='APPROVED', subcategories__products__is_active=True),
            distinct=True
        )
    )
    
    if category_id:
        categories_qs = categories_qs.filter(id=category_id)
    
    categories = categories_qs
    
    context = {
        'all_products': all_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'category_filter': category_id,
        'sort_filter': sort,
        'total_products': all_products.count(),
    }
    
    if request.user.is_authenticated:
        context['data'] = request.user
    
    return render(request, 'core_templates/products.html', context)



