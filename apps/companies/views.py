import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Company, Subscription, StripeEvent
from .forms import CompanySignupForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.users.models import Profile

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


def signup_company(request):
    """Collect company and owner info then start Stripe checkout if needed."""
    if request.method == "POST":
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            company = Company.objects.create(
                name=form.cleaned_data["company_name"],
                slug_subdomain=form.cleaned_data["subdomain"],
                plan=form.cleaned_data["plan"],
            )
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            profile = user.profile
            profile.company = company
            profile.role = "admin"
            profile.save()
            company.created_by = user
            company.save(update_fields=["created_by"])

            if company.plan == "pro":
                session = stripe.checkout.Session.create(
                    mode="subscription",
                    success_url=request.build_absolute_uri(
                        reverse("signup_success")
                    )
                    + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=request.build_absolute_uri(reverse("basic_login")),
                    line_items=[{"price": settings.STRIPE_PRO_PRICE_ID, "quantity": 1}],
                    customer_email=user.email,
                    metadata={"company_id": company.id},
                )
                return redirect(session.url)
            else:
                login(request, user)
                host = f"{company.slug_subdomain}.{request.get_host()}"
                return HttpResponseRedirect(f"//{host}/")
    else:
        form = CompanySignupForm()

    return render(request, "companies/company_signup.html", {"form": form})


def signup_success(request):
    """Handle Stripe checkout success and log the user in."""
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("basic_login")
    session = stripe.checkout.Session.retrieve(session_id)
    company_id = session.metadata.get("company_id")
    company = get_object_or_404(Company, id=company_id)
    company.stripe_customer_id = session.customer
    company.save(update_fields=["stripe_customer_id"])
    if session.subscription:
        Subscription.objects.get_or_create(
            company=company,
            stripe_subscription_id=session.subscription,
            defaults={"status": "active"},
        )
    user = company.created_by
    login(request, user)
    host = f"{company.slug_subdomain}.{request.get_host()}"
    return HttpResponseRedirect(f"//{host}/")


@login_required
def company_info(request):
    if not (request.company and request.user.profile.role == "admin"):
        return HttpResponseForbidden()
    return render(
        request,
        "companies/company_info.html",
        {"company": request.company, "parent": "company", "segment": "info"},
    )

@login_required
def company_users(request):
    if not (request.company and request.user.profile.role == "admin"):
        return HttpResponseForbidden()
    users = Profile.objects.filter(company=request.company).select_related("user")
    return render(
        request,
        "companies/company_users.html",
        {"users": users, "parent": "company", "segment": "users"},
    )
