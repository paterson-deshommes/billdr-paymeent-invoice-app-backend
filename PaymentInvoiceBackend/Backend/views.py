from rest_framework import viewsets
from rest_framework.response import Response
from PaymentInvoiceBackend.Backend.serializers import InvoiceSerializer, InvoiceDetailsSerializer
from rest_framework.exceptions import ValidationError
from stripe.error import InvalidRequestError
import stripe
import os
from datetime import datetime

stripe.api_key = os.getenv("STRIPE_ACCOUNT_TEST_SECRET_KEY")


class InvoiceViewSet(viewsets.ViewSet):
    """
    ViewSet for retrieving invoices
    """

    def list(self, request):
        starting_after = request.query_params.get('starting_after')
        ending_before = request.query_params.get('ending_before')
        limit = request.query_params.get('limit', 10)  # default page size

        if starting_after and ending_before:
            raise ValidationError({
                "detail": "Cannot provide both 'starting_after' and 'ending_before'."
            })
        
        try:
            stripe_invoices = stripe.Invoice.list(limit=limit,starting_after=starting_after,ending_before=ending_before)

            invoiceResultSet = []
            for invoice in stripe_invoices.data:
                invoiceResultSet.append({
                    "id": invoice.id,
                    "amount_due": invoice.amount_due / 100,
                    "amount_paid": invoice.amount_paid / 100,
                    "amount_remaining": invoice.amount_remaining / 100,
                    "currency": invoice.currency,
                    "customer_name": invoice.customer_name,
                    "status": invoice.status
                })

            serializer = InvoiceSerializer(invoiceResultSet, many=True)
            nextCursor = None
            previousCursor = None
            if len(stripe_invoices.data) > 0 and starting_after is None and ending_before is None and stripe_invoices.has_more:
                nextCursor = stripe_invoices.data[-1].id         
            if len(stripe_invoices.data) > 0 and starting_after:
                previousCursor = stripe_invoices.data[0].id
                if stripe_invoices.has_more:
                    nextCursor = stripe_invoices.data[-1].id
            if len(stripe_invoices.data) > 0 and ending_before:
                nextCursor = stripe_invoices.data[-1].id
                if stripe_invoices.has_more:
                    previousCursor = stripe_invoices.data[0].id


            return Response({
                "next": nextCursor,
                "previous": previousCursor,
                "results": serializer.data
                })
        except InvalidRequestError as e:
            raise ValidationError(str(e))

    def retrieve(self, request, pk=None):
        try:
            invoice = stripe.Invoice.retrieve(
                pk,
                expand=["lines.data", "payments.data"]
                )
            invoice_line_items = invoice.lines
            invoice_line_items_result_set = []
            for item in invoice_line_items.auto_paging_iter():
                invoice_line_items_result_set.append({
                    "description": item.description,
                    "amount": item.amount / 100,
                    "quantity": item.quantity,
                    "id": item.id
                })
            invoice_payments = invoice.payments
            invoice_payments_result_set = []
            for payment in invoice_payments.auto_paging_iter():
                invoice_payments_result_set.append({
                    "date": datetime.utcfromtimestamp(payment.created).date(),
                    "amount_paid": payment.amount_paid / 100 if payment.amount_paid else 0,
                    "amount_requested": payment.amount_requested / 100,
                    "status": payment.status,
                    "id": payment.id
                })
            invoiceResult = {
                "id": invoice.id,
                "amount_due": invoice.amount_due / 100,
                "amount_paid": invoice.amount_paid / 100,
                "amount_remaining": invoice.amount_remaining / 100,
                "currency": invoice.currency,
                "customer_id": invoice.customer,
                "customer_name": invoice.customer_name,
                "customer_email": invoice.customer_email,
                "customer_phone": invoice.customer_phone,
                "status": invoice.status,
                "line_items": invoice_line_items_result_set,
                "payments": invoice_payments_result_set
            }
            serializer = InvoiceDetailsSerializer(invoiceResult)
            return Response(serializer.data)
        except InvalidRequestError as e:
            raise ValidationError(str(e))

class PaymentIntentViewSet(viewsets.ViewSet):
    """
    ViewSet for payment intent
    """

    @staticmethod
    def is_integer(value):
        try:
            int(value)  # works for int and float-like strings
            return True
        except (TypeError, ValueError):
            return False
    
    def create(self,request):
        body_params = request.data
        invoice_id = request.data.get("invoice_id")
        customer_id = request.data.get("customer_id")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        if invoice_id is None:
                raise ValidationError({
                    "detail": "invoice_id is required"
                })
        if customer_id is None:
                raise ValidationError({
                    "detail": "customer_id is required"
                })
        if amount is None:
                raise ValidationError({
                    "detail": "amount is required"
                })
        if not self.is_integer(amount):
            raise ValidationError({
                    "detail": "amount must be a valid integer"
                })
        amount = int(amount)
        if amount < 100:
           raise ValidationError({
                    "detail": "Minimal value for amount is 100 cents in the given currency"
                }) 
        if currency is None:
                raise ValidationError({
                    "detail": "currency is required"
                })
        
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)

            if invoice.customer != customer_id:
                raise ValidationError({
                    "detail": f"customer_id {customer_id} does not match the customer associated with the invoice {invoice.id}"
                })
            if invoice.amount_remaining < amount:
                raise ValidationError({
                    "detail": f"cannot charge invoice {invoice.id} more than {float(invoice.amount_remaining) * 100} cents"
                })
            if invoice.currency != currency:
                raise ValidationError({
                    "detail": f"currency {currency} does not match invoice {invoice.id} currency"
                })
            
            payment_intent = stripe.PaymentIntent.create(
                customer = customer_id,
                amount = amount,
                currency = currency,
                automatic_payment_methods={
                    'enabled': True
                }
            )

            stripe.Invoice.attach_payment(
                invoice_id,
                payment_intent = payment_intent.id
            )

            return Response({"client_secret": payment_intent.client_secret})
        except InvalidRequestError as e:
            raise ValidationError(str(e))