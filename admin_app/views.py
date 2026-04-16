from django.http import HttpResponse
from django.shortcuts import render

from core.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from core.models import User


def admindashboard(request):
    return render(request, 'admin_templates/admindashboard.html')

@staff_member_required
def sellerlisting(request):
    sellers = User.objects.filter(role='SELLER').select_related('seller_profile').order_by('-created_at')
    return render(request, 'admin_templates/sellerlisting.html', {
        'sellers': sellers
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
        'customers': customers
    })


def productlisting(request):
    return render(request, 'admin_templates/productlisting.html')

def adminsettings(request):
    return render(request, 'admin_templates/adminsettings.html')

