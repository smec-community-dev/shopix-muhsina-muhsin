from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from seller.models import *

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
        user.phone_number = request.POST.get('phone')
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
    
    # 1. Get or create the main Wishlist container for the user
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, 
        defaults={'wishlist_name': f"{request.user.username}'s Wishlist"}
    )

    # 2. Check if the item already exists in WishlistItem for THIS specific wishlist
    exists = WishlistItem.objects.filter(wishlist=wishlist, variant=variant).exists()

    if exists:
        messages.info(request, "This item is already in your wishlist.")
    else:
        # 3. Create the WishlistItem entry
        WishlistItem.objects.create(wishlist=wishlist, variant=variant)
        messages.success(request, "Added to wishlist!")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
def wishlist_view(request):
    # Fetch the wishlist container for the user
    wishlist = Wishlist.objects.filter(user=request.user).first()
    
    # Fetch all items inside that wishlist (using the related_name="items")
    wishlist_items = []
    if wishlist:
        wishlist_items = wishlist.items.all().select_related('variant', 'variant__product')

    return render(request, 'customer_templates/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, wishlist_item_id):
    """Deletes a specific wishlist entry"""
    # 1. CHANGE: Look in 'WishlistItem' instead of 'Wishlist'
    # 2. CHANGE: Use 'wishlist__user' to traverse the relationship
    item = get_object_or_404(WishlistItem, id=wishlist_item_id, wishlist__user=request.user)
    
    product_name = item.variant.product.name
    item.delete()
    
    messages.success(request, f"{product_name} removed from your wishlist.")
    return redirect('wishlist_view')


@login_required
def clear_wishlist(request):
    """Deletes all items from the user's wishlist without deleting the wishlist itself"""
    # CHANGE: Delete the items inside, not the Wishlist object
    WishlistItem.objects.filter(wishlist__user=request.user).delete()
    
    messages.success(request, "Wishlist cleared successfully.")
    return redirect('wishlist_view')

