import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Company, Subscription, StripeEvent

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        stripe.WebhookSignature.verify_header(payload, sig_header, endpoint_secret)
        event = json.loads(payload)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest()

    if StripeEvent.objects.filter(event_id=event.get('id')).exists():
        return HttpResponse(status=409)
    StripeEvent.objects.create(event_id=event.get('id'))

    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})

    if event_type in ['customer.subscription.updated', 'customer.subscription.deleted']:
        sub_id = data['id']
        status = data.get('status', '')
        subscription = Subscription.objects.filter(stripe_subscription_id=sub_id).first()
        if subscription:
            subscription.status = status
            subscription.save()
            company = subscription.company
            if status not in ['active', 'trialing']:
                company.is_active = False
            else:
                company.is_active = True
            company.grace_until = None
            company.save(update_fields=['is_active', 'grace_until'])

    elif event_type == 'invoice.payment_failed':
        customer_id = data.get('customer')
        company = Company.objects.filter(stripe_customer_id=customer_id).first()
        if company:
            if not company.grace_until:
                company.grace_until = timezone.now() + timezone.timedelta(days=5)
                company.save(update_fields=['grace_until'])
    return HttpResponse('')
