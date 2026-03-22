from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.core.files.storage import default_storage

from .models import *
from .forms import (
    ProductForm,
    ProductImageFormSet,
    VariantFormSet,
    AttributeOptionForm,
    SellerProfileForm
)


# ===================== SELLER HOME =====================
@login_required(login_url='login')
def seller_home_view(request):
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    products = Product.objects.filter(seller=seller_profile)

    return render(request, 'seller_templates/homepage.html', {
        'products': products,
        'seller_profile': seller_profile,
    })


@login_required(login_url='login')
def addproduct(request):
    seller = request.user.seller_profile

    if request.method == "POST":
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES)
        variant_formset = VariantFormSet(request.POST)

        if form.is_valid() and image_formset.is_valid() and variant_formset.is_valid():

            # ✅ SAVE PRODUCT
            product = form.save(commit=False)
            product.seller = seller
            product.save()

            # ✅ SAVE IMAGES (MANUAL FIX)
            files = request.FILES.getlist('image')

            for i, file in enumerate(files):
                ProductImage.objects.create(
                    product=product,
                    image=file,
                    is_primary=True if i == 0 else False
                )

            # ✅ SAVE VARIANTS
            variants = variant_formset.save(commit=False)
            for variant in variants:
                variant.product = product
                variant.save()

            messages.success(request, "Product added successfully")
            return redirect("sellerhome")

        else:
            print("❌ ERRORS:")
            print(form.errors)
            print(image_formset.errors)
            print(variant_formset.errors)

    else:
        form = ProductForm()
        image_formset = ProductImageFormSet()
        variant_formset = VariantFormSet()

    return render(request, "seller_templates/add_product.html", {
        "form": form,
        "image_formset": image_formset,
        "variant_formset": variant_formset,
    })

# ===================== PRODUCT DETAIL =====================
@login_required(login_url='login')
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user.seller_profile)

    return render(request, "seller_templates/product_detail.html", {
        "product": product
    })


# ===================== EDIT PRODUCT =====================
@login_required(login_url='login')
def edit_product(request, slug):
    seller = request.user.seller_profile
    product = get_object_or_404(Product, slug=slug, seller=seller)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        variant_formset = VariantFormSet(request.POST, instance=product)
        
        # FIX: Initialize this here so it exists if validation fails
        attribute_form = AttributeOptionForm(request.POST) 

        if form.is_valid() and image_formset.is_valid() and variant_formset.is_valid():
            # 1. Save core product info
            product = form.save()

            # 2. Handle Images
            deleted_forms = image_formset.deleted_forms
            for del_form in deleted_forms:
                if del_form.instance.image:
                    default_storage.delete(del_form.instance.image.name)
            image_formset.save()

            # 3. Handle Variants
            variants = variant_formset.save(commit=False)
            for variant in variants:
                variant.product = product
                variant.save()
            
            for obj in variant_formset.deleted_objects:
                obj.delete()

            # 4. Handle Attributes
            selected_option_ids = request.POST.getlist("options")
            if selected_option_ids:
                VariantAttributeBridge.objects.filter(variant__product=product).delete()
                product_variants = product.variants.all()
                for v in product_variants:
                    for option_id in selected_option_ids:
                        option = get_object_or_404(AttributeOption, id=option_id)
                        VariantAttributeBridge.objects.create(
                            variant=v,
                            attribute=option.attribute,
                            value=option
                        )

            messages.success(request, f"'{product.name}' updated successfully!")
            return redirect("sellerhome")
        
        else:
            # If we are here, attribute_form is already defined above,
            # so the final render() won't crash anymore.
            messages.error(request, "Please correct the errors below.")

    else:
        # GET request path
        form = ProductForm(instance=product)
        image_formset = ProductImageFormSet(instance=product)
        variant_formset = VariantFormSet(instance=product)
        attribute_form = AttributeOptionForm()

    return render(request, "seller_templates/edit_product.html", {
        "form": form,
        "image_formset": image_formset,
        "variant_formset": variant_formset,
        "attribute_form": attribute_form,
        "product": product
    })
# ===================== SELLER PROFILE =====================
@login_required(login_url='login') 
def sellerprofile(request):
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    products_count = Product.objects.filter(seller=seller_profile).count()

    return render(request, "seller_templates/seller_profile.html", {
        "seller": seller_profile,
        "products_count": products_count,
    })


# ===================== EDIT SELLER PROFILE =====================
@login_required(login_url='login')
def edit_seller_profile(request):
    seller = get_object_or_404(SellerProfile, user=request.user)

    if request.method == "POST":
        form = SellerProfileForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("sellerprofile")
    else:
        form = SellerProfileForm(instance=seller)

    return render(request, "seller_templates/profile_edit.html", {
        "form": form,
        "seller": seller
    })


# ===================== PRODUCT LIST =====================
@login_required(login_url='login')
def productlist(request):
    seller_profile = get_object_or_404(SellerProfile, user=request.user)
    products = Product.objects.filter(seller=seller_profile)

    return render(request, "seller_templates/product_list.html", {
        'products': products,
        'seller_profile': seller_profile,
    })


# ===================== ORDERS =====================
@login_required(login_url='login')
def order_view(request):
    return render(request, "seller_templates/order_view.html")


# ===================== LOGOUT =====================
@login_required(login_url='login')
def seller_logout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def logout_confirm(request):
    return render(request, "seller_templates/logout_confirm.html")
