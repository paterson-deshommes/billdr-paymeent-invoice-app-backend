from rest_framework import serializers

class InvoiceItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    quantity = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()

class InvoicePaymentSerializer(serializers.Serializer):
    id = serializers.CharField()
    date = serializers.CharField()
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_requested = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()

class InvoiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    customer_name = serializers.CharField()
    status = serializers.CharField()

class InvoiceDetailsSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    customer_id = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.CharField()
    customer_phone = serializers.CharField()
    status = serializers.CharField()
    line_items = InvoiceItemSerializer(many=True)
    payments = InvoicePaymentSerializer(many=True)