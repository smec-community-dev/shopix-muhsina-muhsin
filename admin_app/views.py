from django.http import HttpResponse
from django.shortcuts import render

from admin_app.forms import CategoryForm, SubCategoryForm
from core.models import Category, SubCategory, User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from core.models import User


def admindashboard(request):
    sellers = User.objects.filter(role='SELLER').select_related('seller_profile').order_by('-created_at')
    customers = User.objects.filter(role='CUSTOMER')
    sellercount = sellers.count()
    customercount = customers.count()
    return render(request, 'admin_templates/admindashboard.html', {
        'sellercount': sellercount,
        'customercount': customercount,
    })

@staff_member_required
def sellerlisting(request):
    sellers = User.objects.filter(role='SELLER').select_related('seller_profile').order_by('-created_at')
    return render(request, 'admin_templates/sellerlisting.html', {
        'sellers': sellers,
      
    })

@staff_member_required
def seller_detail(request, user_id):
    seller = get_object_or_404(User, id=user_id, role='SELLER')
    return render(request, 'admin_templates/sellerdetail.html', {
        'seller': seller
    })

@staff_member_required
def approve_seller(request, user_id):
    # Fetch the seller
    seller = get_object_or_404(User, id=user_id, role='SELLER')
    
    # 1. Update User model flags
    seller.is_active = True
    seller.is_verified = True
    seller.save()

    # 2. Update the SellerProfile model status (CRITICAL FIX)
    if hasattr(seller, 'seller_profile'):
        profile = seller.seller_profile
        profile.status = 'APPROVED'  # This matches your login check
        profile.save()

    # 3. Send Email
    send_mail(
        'Account Approved',
        f'Hi {seller.first_name}, your shop has been approved. You can now log in.',
        'admin@yourstore.com',
        [seller.email],
        fail_silently=True,
    )

    messages.success(request, f'Seller {seller.email} approved successfully.')
    return redirect('sellerlisting')

@staff_member_required
def reject_seller(request, user_id):
    seller = get_object_or_404(User, id=user_id, role='SELLER')
    
   
    seller.delete()
    
    messages.warning(request, 'Seller application has been rejected and removed.')
    return redirect('sellerlisting')



def customerlisting(request):
    customers = User.objects.filter(role='CUSTOMER')
    return render(request, 'admin_templates/customerlisting.html', {
        'customers': customers,
        
    })


def productlisting(request):
    return render(request, 'admin_templates/productlisting.html')

def adminsettings(request):
    return render(request, 'admin_templates/adminsettings.html')

def categorymanagement(request):
    categories = Category.objects.all()
    return render(request, 'admin_templates/categorymanagement.html', {
        'categories': categories
    })



def add_category(request):
    if request.method == 'POST':
        # request.FILES is required for the image upload
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categorymanagement')
    else:
        form = CategoryForm()
    return render(request, 'admin_templates/category_form.html', {'form': form, 'title': 'Add New'})

def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categorymanagement')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_templates/category_form.html', {'form': form, 'title': 'Edit'})

def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('categorymanagement')

def subcategory_list(request):
    subs = SubCategory.objects.all().select_related('category').order_by('category__name', 'name')
    return render(request, 'admin_templates/subcategorymanagement.html', {'subcategories': subs})

def add_subcategory(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('subcategorymanagement')
    else:
        form = SubCategoryForm()
    return render(request, 'admin_templates/category_form.html', {'form': form, 'title': 'Add Sub-'})

def edit_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, request.FILES, instance=subcategory)
        if form.is_valid():
            form.save()
            return redirect('subcategorymanagement')
    else:
        form = SubCategoryForm(instance=subcategory)
    
    context = {
        'form': form,
        'title': 'Edit Sub-Category',
        'subcategory': subcategory
    }
    return render(request, 'admin_templates/category_form.html', context)

def delete_subcategory(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    
    if request.method == 'POST':
        subcategory.delete()
        
    return redirect('subcategorymanagement')