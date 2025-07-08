import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Company, Subscription, StripeEvent, StripeWebhookLog
from .forms import CompanySignupForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from apps.users.models import Profile

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def handle_stripe_event(event: dict):
    """Process a Stripe event dict."""
    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
        sub_id = data["id"]
        status = data.get("status", "")
        subscription = Subscription.objects.filter(stripe_subscription_id=sub_id).first()
        if subscription:
            subscription.status = status
            subscription.save()
            company = subscription.company
            if status not in ["active", "trialing"]:
                company.life_cycle = Company.LifeCycle.SUSPENDED
            else:
                company.life_cycle = Company.LifeCycle.ACTIVE
            company.grace_until = None
            company.save(update_fields=["life_cycle", "grace_until"])

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        company = Company.objects.filter(stripe_customer_id=customer_id).first()
        if company and not company.grace_until:
            company.grace_until = timezone.now() + timezone.timedelta(days=5)
            company.save(update_fields=["grace_until"])


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        stripe.WebhookSignature.verify_header(payload, sig_header, endpoint_secret)
        event = json.loads(payload)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest()

    if StripeWebhookLog.objects.filter(event_id=event.get("id"), status=StripeWebhookLog.Status.PROCESSED).exists():
        return HttpResponse(status=409)

    log, _ = StripeWebhookLog.objects.get_or_create(event_id=event.get("id"), defaults={"payload": event})
    log.payload = event
    log.save(update_fields=["payload"])

    from .tasks import _handle_webhook  # local import to avoid circular
    _handle_webhook(log)

    return HttpResponse("")


def signup_company(request):
    """Create user and company then send to plan selection."""
    plan = request.GET.get("plan", "free")
    if request.method == "POST":
        form = CompanySignupForm(request.POST)
        if form.is_valid():
            company = Company.objects.create(
                name=form.cleaned_data["company_name"],
                slug_subdomain=form.cleaned_data["subdomain"],
                plan=plan,
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
            login(request, user)
            request.session["onboard_company_id"] = company.id
            return redirect("choose_plan")
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
    request.session.pop("onboard_company_id", None)
    host = f"{company.slug_subdomain}.{request.get_host()}"

    return HttpResponseRedirect(f"//{host}/dashboard/")


@login_required
def choose_plan(request):
    """Display pricing page and start checkout."""
    company_id = request.session.get("onboard_company_id")
    if not company_id:
        return redirect("pricing")
    company = get_object_or_404(Company, id=company_id)
    if request.method == "POST":
        plan = request.POST.get("plan", "free")
        company.plan = plan
        company.save(update_fields=["plan"])
        if plan == "pro":
            session = stripe.checkout.Session.create(
                mode="subscription",
                success_url=request.build_absolute_uri(reverse("signup_success"))
                + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse("choose_plan")),
                line_items=[{"price": settings.STRIPE_PRO_PRICE_ID, "quantity": 1}],
                customer_email=request.user.email,
                metadata={"company_id": company.id},
            )
            return redirect(session.url)
        request.session.pop("onboard_company_id", None)
        host = f"{company.slug_subdomain}.{request.get_host()}"
        return HttpResponseRedirect(f"//{host}/dashboard/")
    return render(
        request,
        "pages/pages/pricing-page.html",
        {"parent": "pages", "segment": "pricing"},
    )


def company_not_found(request):
    return render(request, "companies/company_not_found.html")



@login_required
def company_info(request):
    if not request.company:
        return HttpResponseForbidden()
    if not (
        request.user.is_superuser
        or request.user.has_perm("companies.bypass_tenant_scope")
        or (
            request.user.profile.role == "admin"
            and request.user.profile.company == request.company
        )
    ):

        return HttpResponseForbidden()
    return render(
        request,
        "companies/company_info.html",
        {"company": request.company, "parent": "company", "segment": "info"},
    )

@login_required
def company_users(request):
    if not request.company:
        return HttpResponseForbidden()
    if not (
        request.user.is_superuser
        or request.user.has_perm("companies.bypass_tenant_scope")
        or (
            request.user.profile.role == "admin"
            and request.user.profile.company == request.company
        )
    ):

        return HttpResponseForbidden()
    users = Profile.objects.filter(company=request.company).select_related("user")
    return render(
        request,
        "companies/company_users.html",
        {"users": users, "parent": "company", "segment": "users"},
    )

@login_required
def billing_portal(request):
    if not request.company or not request.company.stripe_customer_id:
        return HttpResponseForbidden()
    session = stripe.billing_portal.Session.create(
        customer=request.company.stripe_customer_id,
        return_url=request.build_absolute_uri(reverse("company_info")),
    )
    return redirect(session.url)


def healthz(request):
    company = getattr(request, "company", None)
    if company and company.life_cycle == Company.LifeCycle.SUSPENDED:
        return HttpResponse("suspended", status=503)
    return HttpResponse("ok")
