from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "price",
            "model_number",
            "subcategory",
            "description",
            "status",   # added
            "is_cancellable",
            "is_returnable",
            "return_days",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "brand": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "price": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "model_number": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "subcategory": forms.Select(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary",
                "rows": 4
            }),
            "status": forms.Select(attrs={     # added
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "return_days": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
        }


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = ["image"]

        widgets = {
            "image": forms.FileInput(attrs={
                "class": "hidden"
            })
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    fields=["image"],
    extra=4,
    can_delete=True
)


class EditProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "price",
            "model_number",
            "subcategory",
            "description",
            "status",   # added
            "is_cancellable",
            "is_returnable",
            "return_days",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "brand": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "price": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "model_number": forms.TextInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "subcategory": forms.Select(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary",
                "rows": 4
            }),
            "status": forms.Select(attrs={   # added
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "return_days": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
        }