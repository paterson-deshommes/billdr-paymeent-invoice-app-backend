import json
from django.http import HttpResponse
import logging
import os
import stripe
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
endpoint_secret = os.getenv("STRIPE_TEST_WEBGOOK_ENDPOINT_SECRET")
stripe.api_key = os.getenv("STRIPE_ACCOUNT_TEST_SECRET_KEY")

@csrf_exempt
def stripe_webhook(request):
  payload = request.body
  event = None

  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)

  if endpoint_secret:
        # Only verify the event if you've defined an endpoint secret
        # Otherwise, use the basic event deserialized with JSON
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

  # Handle the event
  if event.type == 'payment_intent.payment_failed':
    payment_intent = event.data.object # contains a stripe.PaymentIntent
    # Then define and call a method to handle the successful payment intent.
    # handle_payment_intent_succeeded(payment_intent)
    logger.error(f"Payment for payment intent {payment_intent.id} failed")
  elif event.type == 'payment_method.attached':
    payment_method = event.data.object # contains a stripe.PaymentMethod
    # Then define and call a method to handle the successful attachment of a PaymentMethod.
    # handle_payment_method_attached(payment_method)
  # ... handle other event types
  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)