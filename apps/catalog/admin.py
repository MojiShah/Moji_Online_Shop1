from django.contrib import admin
from .models import Category, Product, ProductVariant

# Register your models here.

# --------------------------------
# Product Variant Inline
# --------------------------------

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    min_num=1
    validate_min = True
    fields = ("sku","attributes","price","stock","is_active",)

# --------------------------------
# Category Admin
# --------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name","slug","is_active","created_at",)
    list_filter=("is_active","created_at",)
    search_fields = ("name","slug",)
    ordering = ("name",)
    list_per_page = 25
    
# --------------------------------
# Product Admin
# --------------------------------
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name","category","is_active","created_at",)
    list_filter = ("is_active","category","created_at",)
    search_fields = ("name","slug","short_description","description","variants__sku",)
    readonly_fields = ("created_at","updated_at",)
    inlines = [ProductVariantInline]
    list_select_related = ("category",)
    ordering = ("-created_at",)
    list_per_page = 25
    
# --------------------------------
# Product Variant Admin
# --------------------------------

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = ("sku","product","price","stock","is_active",)
    list_filter = ("is_active","product",)
    search_fields = ("sku","product__name",)
    readonly_fields = ("created_at","updated_at",)
    list_select_related = ("product",)
    list_per_page = 25

# --------------------------------
# Admin Panel Customization
# --------------------------------

admin.site.site_header = "Moji Online Shop Management"
admin.site.site_title = "Moji Admin"
admin.site.index_title = "Store Management Dashboard"

