from django import forms

from core.models import Category, SubCategory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # Added 'slug' to fields
        fields = ['name', 'slug', 'image', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none'}),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-amber-500 outline-none',
                'placeholder': 'Leave blank to auto-generate'
            }),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-gray-300 text-amber-600 focus:ring-amber-500'}),
        }

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        # Added 'slug' to fields
        fields = ['category', 'name', 'slug', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 outline-none'}),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-amber-500 outline-none',
                'placeholder': 'Leave blank to auto-generate'
            }),
            'image': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5 rounded border-gray-300 text-amber-600 focus:ring-amber-500'}),
        }