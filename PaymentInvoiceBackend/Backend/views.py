from rest_framework import viewsets
from rest_framework.response import Response
from PaymentInvoiceBackend.Backend.serializers import InvoiceSerializer, InvoiceDetailsSerializer
from rest_framework.exceptions import ValidationError
from stripe.error import InvalidRequestError
import stripe
import os

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
                expand=["lines.data"]
                )
            invoice_line_items = invoice.lines
            invoice_line_items_result_set = []
            for item in invoice_line_items.auto_paging_iter():
                invoice_line_items_result_set.append({
                    "description": item.description,
                    "amount": item.amount / 100,
                    "quantity": item.quantity
                })
            invoiceResult = {
                "id": invoice.id,
                "amount_due": invoice.amount_due / 100,
                "amount_paid": invoice.amount_paid / 100,
                "amount_remaining": invoice.amount_remaining / 100,
                "currency": invoice.currency,
                "customer_name": invoice.customer_name,
                "customer_email": invoice.customer_email,
                "customer_phone": invoice.customer_phone,
                "status": invoice.status,
                "line_items": invoice_line_items_result_set
            }
            serializer = InvoiceDetailsSerializer(invoiceResult)
            return Response(serializer.data)
        except InvalidRequestError as e:
            raise ValidationError(str(e))