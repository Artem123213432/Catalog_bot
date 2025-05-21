from django.contrib import admin
from .models import (
    ProductCategory,
    ProductSubcategory,
    Product,
    Client,
    Order,
    OrderItem,
    CartItem
)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProductSubcategory)
class ProductSubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'subcategory')
    list_filter = ('subcategory__category', 'subcategory')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('username', 'telegram_id')
    search_fields = ('username', 'telegram_id')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date', 'delivery_address')
    list_filter = ('date',)
    search_fields = ('client__username', 'delivery_address')
    inlines = [OrderItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('client', 'product', 'quantity')
    list_filter = ('client',)
    search_fields = ('client__username', 'product__name')
