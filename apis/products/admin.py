# products/admin.py
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)} # Automatically fills slug based on name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'categories', 'created_at', 'updated_at'] # Filters in the sidebar
    list_editable = ['price', 'stock', 'available'] # Allows editing directly from the list view
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('categories',) # For ManyToMany, provides a lookup widget if many categories
    date_hierarchy = 'created_at' # Adds navigation by date
    search_fields = ['name', 'description'] # Adds a search box