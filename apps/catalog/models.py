import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Category(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140,unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(
                fields=["is_active", "name"],
                name="category_active_name_idx"
            )]
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name
    
class Product(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220,unique=True)
    short_description = models.CharField(max_length=300,blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/%Y/%m/",blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["category", "is_active"],
                name="product_category_active_idx"
            ),
            models.Index(
                fields=["is_active", "created_at"],
                name="product_active_created_idx"
            )
        ]

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
    

class ProductVariant(models.Model):

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="variants")
    sku = models.CharField(max_length=64,unique=True)
    attributes = models.JSONField(default=dict,blank=True)
    price = models.DecimalField(max_digits=12,decimal_places=2,validators=[MinValueValidator(Decimal("0.01"))])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attributes"],
                name="uniq_variant_attrs_product"
            ),
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="variant_price_gt_zero"
            )
        ]

        indexes = [
            models.Index(
                fields=["product", "is_active"],
                name="variant_prod_active_idx"
            ),
            models.Index(
                fields=["is_active", "price"],
                name="variant_active_price_idx"
            )
        ]

        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

