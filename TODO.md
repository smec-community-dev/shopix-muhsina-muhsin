# Product Save Fix - Approved Plan

## Steps:

### 1. Update seller/forms.py
- Change VariantFormSet extra=1 → extra=0 (make variants optional)

### 2. Update seller/views.py
- Ensure seller_profile exists for user
- Make image/variant formsets optional (validate but allow empty)
- Add subcategory queryset check
- Improve error messages

### 3. Test
- Run `python manage.py runserver`
- Go to seller/product/add/
- Fill minimal product form (skip variants/images)
- Submit and check console/page/DB

### 4. Verify DB
- `python manage.py shell`
- `from seller.models import Product; Product.objects.all()`

### 5. Handle remaining issues
- If subcategory empty: create some
- Migrate if needed

**Current Progress:** Creating TODO.md ✅

