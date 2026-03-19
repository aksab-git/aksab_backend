from rest_framework import serializers
from .models.mainInventory import InventoryItem
from .models.transactions import StockTransfer

class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    unit = serializers.ReadOnlyField(source='product.unit')

    class Meta:
        model = InventoryItem
        fields = ['id', 'product_name', 'unit', 'stock_quantity', 'last_updated']

class StockTransferSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    sender_name = serializers.ReadOnlyField(source='sender_warehouse.name')

    class Meta:
        model = StockTransfer
        fields = ['id', 'sender_name', 'product_name', 'quantity', 'status', 'created_at']

