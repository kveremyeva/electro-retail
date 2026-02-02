from rest_framework import serializers

from .models import Contact, Product, Provider


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'email', 'country', 'city', 'street', 'house']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'product_model', 'release_date']


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            'id',
            'name',
            'node_type',
            'contact_info',
            'products',
            'supplier',
            'debt_to_supplier',
            'created_at',
            'hierarchy_level'
        ]
        read_only_fields = ['debt_to_supplier', 'created_at', 'hierarchy_level']
