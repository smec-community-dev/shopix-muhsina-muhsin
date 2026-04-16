from datetime import timedelta
from django.utils import timezone
import os
import random
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.storage import default_storage

from core.adapter import get_redirect_by_role
from customer.models import WishlistItem
from seller.models import ProductVariant
from core.models import Category, User
from seller.models import SellerProfile

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

def login_view(request):
    show_google_login = True 

    if request.method == "POST":
        email_input = request.POST.get('login') # This is the email field from your form
        password = request.POST.get('password')

        # 1. Manually find the user by email
        try:
            user = User.objects.get(email=email_input)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return render(request, 'core_templates/loginpage.html', {'show_google_login': show_google_login})

        # 2. Check the password manually
        if check_password(password, user.password):
            
            # 3. Check if the "is_active" flag is True (The Django Admin checkbox)
            if not user.is_active:
                messages.error(request, 'Your account is disabled. Please contact admin.')
                return render(request, 'core_templates/loginpage.html', {'show_google_login': show_google_login})

            # 4. SELLER SPECIFIC: Check profile approval
            if hasattr(user, 'role') and user.role == 'SELLER':
                try:
                    if user.seller_profile.status != 'APPROVED':
                        messages.error(request, "Your seller profile is pending admin approval.")
                        return render(request, 'core_templates/loginpage.html', {'show_google_login': show_google_login})
                except AttributeError:
                    messages.error(request, "Seller profile not found.")
                    return render(request, 'core_templates/loginpage.html', {'show_google_login': show_google_login})

            # 5. AUTHENTICATION SUCCESS
            # We must specify the backend because we bypassed authenticate()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(get_redirect_by_role(user))
        
        else:
            messages.error(request, 'Incorrect password.')

    return render(request, 'core_templates/loginpage.html', {
        'show_google_login': show_google_login
    })

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
        data = request.POST
        files = request.FILES
        
        # 1. Validation
        if data.get('password') != data.get('confirm_password'):
            messages.error(request, 'Passwords do not match.')
            return render(request, 'core_templates/seller_register.html')

        if User.objects.filter(email=data.get('email')).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'core_templates/seller_register.html')

        # 2. Handle Temporary Documents
        doc1 = files.get('document_1')
        doc2 = files.get('document_2')
        path1 = default_storage.save(f'tmp/{doc1.name}', ContentFile(doc1.read())) if doc1 else None
        path2 = default_storage.save(f'tmp/{doc2.name}', ContentFile(doc2.read())) if doc2 else None

        # 3. Store in Session (Keys here must match verify_otp exactly)
        otp = str(random.randint(100000, 999999))
        request.session['register_data'] = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'password': data.get('password'),
            'role': 'SELLER',
            'store_name': data.get('shop_name'),
            'business_address': data.get('business_address'),
            'gst_number': data.get('gst_number'),
            'pan_number': data.get('pan_number'),
            'bank_account_number': data.get('account_number'),
            'ifsc_code': data.get('ifsc_code'),
            'branch_name': data.get('branch_name'),
            'doc1_path': path1,
            'doc2_path': path2,
        }
        request.session['otp'] = otp

        send_mail('Verify Email', f'OTP: {otp}', settings.EMAIL_HOST_USER, [data.get('email')])
        return redirect('verify_otp')

    return render(request, 'core_templates/seller_register.html')

def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        data = request.session.get('register_data')

        # 1. Session Integrity Check
        if not data or not session_otp:
            messages.error(request, "Session expired or invalid registration attempt.")
            return redirect('login')

        # 2. OTP Verification
        if user_otp == session_otp:
            try:
                # 3. Create the User (Inactive by default)
                user = User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    phone_number=data.get('phone'),
                    role=data.get('role', 'CUSTOMER'),
                    is_active=False  # Blocks login until admin approval
                )

                # 4. Handle Seller Specific Logic
                if data.get('role') == 'SELLER':
                    # Create Profile with PENDING status
                    profile = SellerProfile.objects.create(
                        user=user,
                        store_name=data['store_name'],
                        business_address=data['business_address'],
                        gst_number=data['gst_number'],
                        pan_number=data['pan_number'],
                        bank_account_number=data['bank_account_number'],
                        ifsc_code=data['ifsc_code'],
                        branch_name=data.get('branch_name'),
                        status='PENDING' # Explicitly set status
                    )

                    # 5. Move Files from Temp to Permanent Storage
                    # Map session keys to model fields
                    document_map = [
                        ('doc1_path', 'document_1'),
                        ('doc2_path', 'document_2')
                    ]

                    for session_key, model_field_name in document_map:
                        temp_path = data.get(session_key)
                        if temp_path and default_storage.exists(temp_path):
                            with default_storage.open(temp_path) as f:
                                # Get the file field from the profile instance
                                field = getattr(profile, model_field_name)
                                # Save it (this moves it to MEDIA_ROOT/seller_docs/)
                                field.save(os.path.basename(temp_path), File(f), save=True)
                            
                            # Clean up the temporary file
                            default_storage.delete(temp_path)

                else:
                    # If it's a customer, you might want to auto-activate them
                    user.is_active = True
                    user.save()

                # 6. Cleanup Session
                del request.session['otp']
                del request.session['register_data']

                messages.success(request, "Registration successful! You can login only after admin approves you.")
                return redirect('login')

            except Exception as e:
                # Handle unexpected database errors (like unique constraint failures)
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'core_templates/verify_otp.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def home_view(request):
    # Optimized Query: Fetch variants with their associated products and images in a single/few queries
    products = ProductVariant.objects.select_related(
        'product', 'product__subcategory'
    ).prefetch_related(
        'product__images'
    ).filter(product__is_active=True).order_by('-created_at')[:20] # Limiting to 20 for homepage performance

    user_wishlist_ids = [] 

    if request.user.is_authenticated:
        user_wishlist_ids = list(WishlistItem.objects.filter(
            wishlist__user=request.user
        ).values_list('variant_id', flat=True))

    print(products)
    context = {
        'products': products,
        'user_wishlist_ids': user_wishlist_ids,
    }
    
    return render(request, 'core_templates/homepage.html', context)

# def home_view(request):
#     products = ProductVariant.objects.filter(
#         product__approval_status='APPROVED',
#         product__is_active=True
#     ).select_related('product').prefetch_related('images')

#     user_wishlist_ids = [] 

#     if request.user.is_authenticated:
#         user_wishlist_ids = WishlistItem.objects.filter(
#             wishlist__user=request.user
#         ).values_list('variant_id', flat=True)

#     context = {
#         'products': products,
#         'user_wishlist_ids': list(user_wishlist_ids),
#     }
    
#     return render(request, 'core_templates/homepage.html', context)



def single_variant_view(request, id):
    """Render HTML for a single product variant."""
    variant = get_object_or_404(
        ProductVariant.objects.select_related('product__seller', 'product__subcategory')
                              .prefetch_related('product__images'),
        id=id
    )
    context = {
        'variant': variant,
    }
    return render(request, 'customer_templates/single_fetch.html', context)



def core_product(request):
    """View to display products page with New Arrivals section and All Products section"""
    from django.db.models import Count, Q
    
    # Get filter/sort params
    category_id = request.GET.get('category_id')
    sort = request.GET.get('sort', 'newest')
    
    # Base queryset for all approved/active products
    base_qs = ProductVariant.objects.filter(
        product__approval_status='APPROVED',
        product__is_active=True
    ).select_related('product', 'product__subcategory__category').prefetch_related('product__images')
    
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
    
    return render(request, 'core_templates/core_product.html', context)



