from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages

from seller.models import Product, SellerProfile

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
    products = Product.objects.all()
    

    user=request.user
    if user.is_authenticated:
        return render(request, 'core_templates/homepage.html', { 'products' : products })
    return render(request, 'core_templates/homepage.html', { 'products' : products })
