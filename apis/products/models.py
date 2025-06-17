from django.db import models
from django.utils.text import slugify # For creating URL-friendly slugs
from django.urls import reverse # For get_absolute_url

class Category(models.Model):
    """
    Represents a category for products (e.g., Technology, Fashion).
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Category Description")

    class Meta:
        verbose_name_plural = "Categories" # Correct plural name for admin interface
        ordering = ['name'] # Order categories alphabetically by name

    def save(self, *args, **kwargs):
        """Generates a slug from the name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to the category detail page."""
        return reverse('product_list_by_category', args=[self.slug])


class Product(models.Model):
    """
    Represents a single product in the mini-mart.
    """
    # Product Core Information
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., 700.00 - crucial for currency
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True) # Requires Pillow library
    description = models.TextField(blank=True)

    # Inventory and Availability
    stock = models.PositiveIntegerField(default=0) # Number of items currently in stock
    available = models.BooleanField(default=True) # Whether the product is currently available for purchase

    # Relationships
    # A product can belong to multiple categories (e.g., a smart watch could be 'Technology' and 'Fashion')
    categories = models.ManyToManyField(Category, related_name='products')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Automatically sets the creation timestamp
    updated_at = models.DateTimeField(auto_now=True) # Automatically updates the timestamp on each save

    class Meta:
        ordering = ['name'] # Default ordering for products
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']), # Index for latest products
        ]

    def save(self, *args, **kwargs):
        """Generates a slug from the name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the URL to the product detail page."""
        return reverse('product_detail', args=[self.slug])