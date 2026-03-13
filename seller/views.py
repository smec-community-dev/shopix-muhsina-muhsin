from django.shortcuts import get_object_or_404, render,redirect
from seller.forms import EditProductForm, ProductForm, ProductImageFormSet
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core import urls
from django.contrib.auth import logout

@login_required(login_url='login')
def seller_home_view(request):
    
    seller_profile = get_object_or_404(SellerProfile, user=request.user)

    products = Product.objects.filter(seller=seller_profile)
    print(seller_profile)

    return render(request, 'seller_templates/homepage.html',{
        'products': products,
        'seller_profile':seller_profile,
    })



@login_required(login_url='login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "seller_templates/product_detail.html", {"product": product})

@login_required(login_url='login')
def sellerprofile(request):
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    products_count = Product.objects.filter(seller=seller_profile).count()

    return render(request, "seller_templates/seller_profile.html", {
        "seller": seller_profile,
        "products_count": products_count,
    })

@login_required(login_url='login')
def addproduct(request):

    seller = request.user.seller_profile

    if request.method == "POST":

        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():

            product = form.save(commit=False)
            product.seller = seller
            product.save()

            images = formset.save(commit=False)

            for image in images:
                image.product = product
                image.save()

            return redirect("sellerhome")

    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, "seller_templates/add_product.html", {
        "form": form,
        "formset": formset
    })


@login_required(login_url='login')
def edit_product(request, slug):

    seller = request.user.seller_profile
    product = get_object_or_404(Product, slug=slug, seller=seller)

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid() and formset.is_valid():

            form.save()
            formset.save()

            return redirect("sellerhome")

    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(request, "seller_templates/edit_product.html", {
        "form": form,
        "formset": formset,
        "product": product
    })

@login_required(login_url='login')
def seller_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def logout_confirm(request):
    return render(request, "seller_templates/logout_confirm.html")