from rest_framework import serializers

class InvoiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    amount_remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    customer_name = serializers.CharField()
    status = serializers.CharField()
    public_invoice_link = serializers.URLField(required=False, allow_null=True)  # optional