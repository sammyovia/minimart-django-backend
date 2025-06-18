from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    categories_read = CategorySerializer(many=True, read_only=True, source='categories')
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), write_only=True, source='categories'
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'image', 'description',
            'stock', 'available', 'categories_read', 'category_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        product = Product.objects.create(**validated_data)
        product.categories.set(categories_data)
        return product

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categories_data is not None:
            instance.categories.set(categories_data)
        return instance