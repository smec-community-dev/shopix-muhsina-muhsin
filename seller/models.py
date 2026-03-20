import uuid
from django.db import models
from django.utils.text import slugify

class SellerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="seller_profile")
    store_name = models.CharField(max_length=255)
    store_slug = models.SlugField(unique=True)
    gst_number = models.CharField(max_length=50)
    pan_number = models.CharField(max_length=50)
    bank_account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    business_address = models.TextField()
    rating = models.FloatField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.store_name:
            return self.store_name
        return self.user.username



class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey("seller.SellerProfile", on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey("core.SubCategory", on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)

    # status = models.CharField(
    #     max_length=10,
    #     choices=STATUS_CHOICES,
    #     default='ACTIVE'
    # )

    is_cancellable = models.BooleanField(default=True)
    is_returnable = models.BooleanField(default=True)
    return_days = models.IntegerField(default=7)

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
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    slug = models.SlugField(unique=True, blank=True)  
    sku_code = models.CharField(max_length=100, unique=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.FloatField(null= True,default=0.0)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    weight = models.FloatField(help_text="Weight in kg")
    length = models.FloatField(help_text="Length in cm")
    width = models.FloatField(help_text="Width in cm")
    height = models.FloatField(help_text="Height in cm")
    tax_percentage = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.product.name}-{self.sku_code}")
            slug = base_slug
            counter = 1
            while ProductVariant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.sku_code}"

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("seller.Product", on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    variant = models.ForeignKey("seller.ProductVariant", on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    image = models.ImageField(upload_to='product_images',null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        if self.variant:
            return f"Image for {self.variant.sku_code}"
        return f"Image for {self.product.name}"

class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class AttributeOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class VariantAttributeBridge(models.Model):
    variant = models.ForeignKey("seller.ProductVariant", on_delete=models.CASCADE)
    option = models.ForeignKey(AttributeOption, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.variant.sku_code} - {self.option}"

class InventoryLog(models.Model):
    variant = models.ForeignKey("seller.ProductVariant", on_delete=models.CASCADE)
    change_amount = models.IntegerField()
    reason = models.CharField(max_length=50)
    performed_by = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.variant.sku_code} ({self.change_amount})"