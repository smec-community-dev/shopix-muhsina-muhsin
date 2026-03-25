# Resolve Project Errors - BLACKBOXAI Plan

Status: [ ] In Progress

## Step 1: [ ] Fix Allauth Deprecations (pro1/pro1/settings.py)
- Replace deprecated ACCOUNT_* settings with new format
- Expected: `python manage.py check` shows no warnings

## Step 2: [x] Fix Add Product Formsets (pro1/seller/views.py)
- Use image_formset.save() instead of manual FILES loop
- Ensure consistent with edit_product view
- Test: Seller add product succeeds without console errors ✓

## Step 3: [x] Cleanup Duplicate Code (pro1/admin_app/views.py)
- Remove commented/broken register/login views (handled in core/views.py) ✓

## Step 4: [x] Run Django Commands
- `cd pro1 && python manage.py makemigrations && python manage.py migrate`
- `cd pro1 && python manage.py check`
- `cd pro1 && python manage.py collectstatic --noinput` ✓

## Step 5: [ ] Test Core Features
- Run `cd pro1 && python manage.py runserver`
- Test buyer register + OTP email
- Test login (email/pass)
- Seller: add product
- Browse home/products

## Step 6: [x] Update TODO Files
- Mark TODO_login_fix.md, TODO_add_product_fix.md complete ✓

**Next**: Complete Step 1 → update [x] → Step 2 etc.

