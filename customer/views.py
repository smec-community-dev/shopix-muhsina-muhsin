from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from seller.models import *
from core .models import *
from decimal import Decimal
import uuid





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


@login_required 
def customer_address(request):
    address= Address.objects.filter(user=request.user)
    return render(request,'customer_templates/customer_address.html',{'address':address})

@login_required 
def customer_address_add(request):
    if request.method=="POST":
        address_obj=Address()
        address_obj.user=request.user
        address_obj.full_name=request.POST.get('full_name')
        address_obj.phone_number=request.POST.get('phone_number')
        address_obj.pincode=request.POST.get('pincode')
        address_obj.house_info=request.POST.get('house_info')
        address_obj.locality=request.POST.get('locality')
        address_obj.city=request.POST.get('city')
        address_obj.state=request.POST.get('state')
        address_obj.landmark=request.POST.get('landmark')
        address_obj.landmark = request.POST.get('landmark', '')
        address_obj.address_type=request.POST.get('adress_type')
        is_default= request.POST.get('is_default')=='on'

        if not Address.objects.filter(user=request.user).exists():
            is_default=True

        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        address_obj.is_default= is_default

        address_obj.save()

        messages.success(request,"Address added successfully")
        return redirect('customer_address')
    return render(request,'customer_templates/customer_address_add.html')


@login_required 
def customer_address_update(request,address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    if request.method == "POST":
        address.full_name = request.POST.get('full_name')
        address.phone_number = request.POST.get('phone_number')
        address.pincode = request.POST.get('pincode')
        address.house_info = request.POST.get('house_info')
        address.locality = request.POST.get('locality')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.landmark = request.POST.get('landmark')
        address.address_type = request.POST.get('address_type', 'HOME')
        is_default = request.POST.get('is_default') == 'on'
        

        if is_default:

            Address.objects.filter(user=request.user, is_default=True).exclude(id=address_id).update(is_default=False)
            address.is_default = True
        else:

            if not Address.objects.filter(user=request.user).exclude(id=address_id).exists():
                address.is_default = True
            else:
                address.is_default = False

        address.save()
        
        messages.success(request, "Address updated successfully!")
        return redirect('customer_address')

    return render(request, 'customer_templates/customer_address_update.html', {'address': address})




@login_required
def customer_address_delete(request, address_id):
    address = Address.objects.get(id=address_id, user=request.user)
    
    was_default = address.is_default
    

    address.delete()
    
    if was_default:
        remaining_address = Address.objects.filter(user=request.user).first()
        if remaining_address:
            remaining_address.is_default = True
            remaining_address.save()
            messages.info(request, "Primary address deleted. A new default has been assigned.")
        else:
            messages.info(request, "Address deleted. You currently have no saved addresses.")
    else:
        messages.success(request, "Address removed successfully.")

    return redirect('customer_address')




@login_required
def order(request, id):
    product = get_object_or_404(Product, id=id)
    product_variant = ProductVariant.objects.get(product=product)
    
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
    
    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()
    
    return render(request, 'customer_templates/order.html', {
        'order': product_variant,
        'addresses': addresses,
        'default_address': default_address
    })


@login_required
def checkout(request, cart_id):
    user = request.user
    cart = get_object_or_404(Cart, id=cart_id, user=user)
    cart_items = CartItem.objects.filter(cart=cart)

    addresses = Address.objects.filter(user=user).order_by('-is_default', '-updated_at')

    default_address = addresses.filter(is_default=True).first()
    if not default_address:
        default_address = addresses.first()

    subtotal = sum(item.price_at_time * item.quantity for item in cart_items)
    
    tax = round(Decimal(str(subtotal)) * Decimal('0.08'), 2) 
    
    grand_total = Decimal(str(subtotal)) + tax 

    return render(request, 'customer_templates/order.html', {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'is_cart_checkout': True
    })


@login_required
def order_select_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    
    product_id = request.GET.get('product_id')
    if product_id:
        return redirect('order', id=product_id)
    return redirect('order')



@login_required
def place_order(request):
    user=request.user
    if request.method !="POST":
        return redirect("home")
    
    variant_id=request.POST.get("variant_id")
    cart_id=request.POST.get("cart_id")
    payment_method=request.POST.get("payment_method")
    
    address=Address.objects.filter(user=user, is_default=True).first()

    if not address:
        messages.error(request,"Please Add a Delivery Address.")
        return redirect("customer_add_address")
    
    order_number="ORD-" + uuid.uuid4().hex[:10].upper()
    
  
    if cart_id:
        cart = get_object_or_404(Cart, id=cart_id, user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            messages.error(request,"Your cart is empty.")
            return redirect("cart")
        
        total_amount = sum(item.price_at_time * item.quantity for item in cart_items)
        
       
        order=Order.objects.create(
            user=user,
            order_number=order_number,
            total_amount=total_amount,
            payment_method=payment_method,
            address=address
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                seller=item.variant.product.seller,
                quantity=item.quantity,
                price_at_purchase=item.price_at_time
            )
        #cart_delete
        cart_items.delete()
        cart.total_amount = 0
        cart.save()
        
        messages.success(request,f"ORDER Placed Successfully! Order Number: {order_number}")
        return redirect("order_confirmation", order_id=order.id)
    

    if not variant_id:
        messages.error(request,"Invalid order request.")
        return redirect("customer_home")
    
    variant=get_object_or_404(ProductVariant, id=variant_id)
    
    order=Order.objects.create(
        user=user,
        order_number=order_number,
        total_amount=variant.selling_price,
        payment_method=payment_method,
        address=address
    )
    OrderItem.objects.create(
        order=order,
        variant=variant,
        seller=variant.product.seller,
        quantity=1,
        price_at_purchase=variant.selling_price
    )
    messages.success(request,f"ORDER Placed SuccessFully! Order Number: {order_number}")
    return redirect("order_confirmation", order_id=order.id)


@login_required
def order_confirmation(request,order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_item=OrderItem.objects.filter(order=order)
    return render(request,"customer_templates/order_confirmation.html",{"order":order,"order_item":order_item})
