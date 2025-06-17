# products/serializers.py
from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' # Includes 'id', 'name', 'slug', 'description'

class ProductSerializer(serializers.ModelSerializer):
    # To display category names instead of just their IDs in the product list/detail
    categories = CategorySerializer(many=True, read_only=True)
    # If you want to allow updating categories by their IDs, you'd add:
    # category_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all(), source='categories', write_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'image', 'description',
            'stock', 'available', 'categories', 'created_at', 'updated_at'
        ]
        # Or simply fields = '__all__' if you want all model fields
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at'] # These fields are typically not set by the client

    # If you manually defined 'categories' field above, you might need to handle saving it
    def create(self, validated_data):
        categories_data = validated_data.pop('categories', []) # Remove categories data if passed
        product = Product.objects.create(**validated_data)
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(**category_data)
            product.categories.add(category)
        return product

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None) # Pop categories data if present

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update categories if provided
        if categories_data is not None:
            instance.categories.clear() # Clear existing categories
            for category_data in categories_data:
                category, created = Category.objects.get_or_create(name=category_data.get('name')) # Or use ID lookup
                instance.categories.add(category)

        return instance