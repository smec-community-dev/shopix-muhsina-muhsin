from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

