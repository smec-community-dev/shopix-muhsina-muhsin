from django.db import models
from core.models import User, SubCategory
from django.utils.text import slugify


# ================= SELLER =================
from django.db import models
from django.utils.text import slugify
from core.models import User

from django.db import models
from django.utils.text import slugify

from django.db import models
from django.conf import settings
from django.utils.text import slugify

class SellerProfile(models.Model):
    # Status choices for admin approval workflow
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # Link to the custom User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='seller_profile'
    )
    
    # Store Information
    store_name = models.CharField(max_length=255)
    store_slug = models.SlugField(unique=True, blank=True)
    business_address = models.TextField()
    
    # Verification & Status (The logic you requested)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    is_verified = models.BooleanField(default=False)
    
    # Tax & Identity Details
    gst_number = models.CharField(max_length=15)
    pan_number = models.CharField(max_length=10)
    
    # Banking Details
    bank_account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    branch_name = models.CharField(max_length=100)
    
    # Document Uploads
    document_1 = models.FileField(upload_to='seller_docs/', null=True, blank=True)
    document_2 = models.FileField(upload_to='seller_docs/', null=True, blank=True)
    
    # Metrics (Fixed the IntegrityError by adding default=0.0)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically generate slug from store name if not provided
        if not self.store_slug:
            self.store_slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.store_name} ({self.user.email})"

# ================= PRODUCT =================
class Product(models.Model):

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    model_number = models.CharField(max_length=100)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    approval_status = models.CharField(
        max_length=20,
        choices=(
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ),
        default='PENDING'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ================= VARIANT =================
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku_code = models.CharField(max_length=100, unique=True)

    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_quantity = models.IntegerField(default=0)

    # ✅ FIXED: OPTIONAL FIELDS
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    length = models.FloatField(null=True, blank=True, help_text="Length in cm")
    width = models.FloatField(null=True, blank=True, help_text="Width in cm")
    height = models.FloatField(null=True, blank=True, help_text="Height in cm")

    tax_percentage = models.FloatField(default=0)

    is_cancellable = models.BooleanField(default=True)
    is_returnable = models.BooleanField(default=True)
    return_days = models.IntegerField(default=7)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sku_code


# ================= PRODUCT IMAGE =================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="productimages/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"


# ================= ATTRIBUTES =================
class Attribute(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"


class VariantAttributeBridge(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    option = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.variant.sku_code} - {self.option.value}"


# ================= INVENTORY =================
class InventoryLog(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=50)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant.sku_code} ({self.change_amount})"
    
# class OrderItem(models.Model):
#     order = models.ForeignKey("customer.Order", on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey("seller.Product", on_delete=models.CASCADE)
#     seller = models.ForeignKey("seller.SellerProfile", on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)