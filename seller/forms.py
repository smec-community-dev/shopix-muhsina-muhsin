from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "model_number",
            "subcategory",
            "description",
            "approval_status",  # Matches your model's field name
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
            "approval_status": forms.Select(attrs={
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


# Cleaned up the FormSet by removing Git merge markers (<<<<, ====, >>>>)
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=4,
    fk_name='product',
    can_delete=True
)


class EditProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "brand",
            "model_number",
            "subcategory",
            "description",
            "approval_status",
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
            "approval_status": forms.Select(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
            "return_days": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border-gray-300 focus:ring-primary focus:border-primary"
            }),
        }