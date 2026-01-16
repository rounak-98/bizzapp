"""
Core serializers placeholder.

If you plan to build an API with Django REST Framework add serializers
here. Keep this file to avoid import errors from other modules.
"""

try:
    from rest_framework import serializers

    from .models import Customer, Item, Quotation

    class CustomerSerializer(serializers.ModelSerializer):
        class Meta:
            model = Customer
            fields = ["id", "name", "email", "phone"]

    class ItemSerializer(serializers.ModelSerializer):
        class Meta:
            model = Item
            fields = ["id", "name", "description", "quantity", "price"]

    class QuotationSerializer(serializers.ModelSerializer):
        class Meta:
            model = Quotation
            fields = ["id", "customer", "date"]

except Exception:
    # DRF not installed or models not available in some contexts
    pass
