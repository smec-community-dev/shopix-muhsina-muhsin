from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from seller.models import *

User = get_user_model()

# @login_required(login_url='login')
# def customer_home_view(request):
#     products = Product.objects.all()
#     return render(request, 'core_templates/homepage.html', { 'products' : products })


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')

        # Username
        new_username = (request.POST.get('username') or '').strip()
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, "This username is already taken by another account.")
                return redirect('profile')
            user.username = new_username

        # Email
        new_email = (request.POST.get('email') or '').strip()
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(request, "This email is already taken by another account.")
                return redirect('profile')
            user.email = new_email

        # Phone
        phone = (request.POST.get('phone') or '').strip()
        if phone:
            # Ensure uniqueness across all users (excluding the current user)
            if User.objects.filter(phone_number=phone).exclude(pk=user.pk).exists():
                messages.error(request, "This phone number is already taken by another account.")
                return redirect('profile')
            user.phone_number = phone
        else:
            user.phone_number = None

        image = request.FILES.get('profile_image')
        if image:
            user.profile_image = image
        user.save()

        messages.success(request, "Profile updated successfully")
        return redirect('profile')  

    return render(request, 'customer_templates/profilepage.html', {'user': user})


def dashboard_view(request):
    products = Product.objects.all()
    return render(request, 'customer_templates/coustomer_dashboard.html', {
        'products': products
    })
    

@login_required
def cart_view(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items = CartItem.objects.filter(cart=cart).select_related('variant__product')
    total_amount=sum(item.quantity * item.price_at_time for item in cart_items)
    return render(request,'customer_templates/cart.html',{
        'cart': cart,
        'cart_items': cart_items,
        'total_amount': total_amount
    })

@login_required
def add_cart(request,variant_id):
    user=request.user
    variant=get_object_or_404(ProductVariant,id=variant_id)
    cart=get_object_or_404(Cart,user=user)
    cart_item,create=CartItem.objects.get_or_create(cart=cart,variant=variant,defaults={'quantity':1,'price_at_time':variant.selling_price})
    if not create:
        cart_item.quantity+=1
        cart_item.price_at_time=variant.selling_price
        cart_item.save()
        return redirect('home')
    return redirect('home')


@login_required
def cart_update_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
            
    return redirect('cart')


@login_required
def cart_remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('cart')



def variant_page(request, id):
    variant = get_object_or_404(
        ProductVariant.objects.select_related('product__seller').prefetch_related(
            'product__images',
            'images'
        ),
        id=id
    )
    return render(request, 'customer_templates/single_fetch.html', {'variant': variant})




@login_required
def add_to_wishlist(request, variant_id):
    if not request.user.is_authenticated:
        return redirect('login')

    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, 
        defaults={'wishlist_name': f"{request.user.username}'s Wishlist"}
    )

   
    exists = WishlistItem.objects.filter(wishlist=wishlist, variant=variant).exists()

    if exists:
        messages.info(request, "This item is already in your wishlist.")
    else:

        WishlistItem.objects.create(wishlist=wishlist, variant=variant)
        messages.success(request, "Added to wishlist!")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlist_items = []
    if wishlist:
        wishlist_items = wishlist.items.all().select_related('variant', 'variant__product')

    return render(request, 'customer_templates/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, wishlist_item_id):
    """Deletes a specific wishlist entry"""
    item = get_object_or_404(WishlistItem, id=wishlist_item_id, wishlist__user=request.user)
    
    product_name = item.variant.product.name
    item.delete()
    
    messages.success(request, f"{product_name} removed from your wishlist.")
    return redirect('wishlist_view')


@login_required 
def clear_wishlist(request):
    """Deletes all items from the user's wishlist without deleting the wishlist itself"""

    WishlistItem.objects.filter(wishlist__user=request.user).delete()
    
    messages.success(request, "Wishlist cleared successfully.")
    return redirect('wishlist_view')
