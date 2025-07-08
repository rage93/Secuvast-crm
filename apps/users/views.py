from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from django.urls import reverse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import Http404
from django.contrib.auth import login

from apps.users.forms import (
    ProfileForm,
    QuillFieldForm,
    TenantUserCreationForm,
    InviteUserForm,
)
from apps.users.models import Profile
from apps.companies.models import Company

signer = TimestampSigner()


@login_required(login_url="/accounts/basic-login/")
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = QuillFieldForm(instance=profile)
    if request.method == "POST":
        if request.POST.get("email"):
            request.user.email = request.POST.get("email")
            request.user.save()

        for attribute, value in request.POST.items():
            if attribute == "csrfmiddlewaretoken":
                continue
            setattr(profile, attribute, value)
        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect(request.META.get("HTTP_REFERER"))

    context = {"segment": "profile", "parent": "apps", "form": form}
    return render(request, "pages/apps/user-profile.html", context)


@login_required(login_url="/accounts/basic-login/")
def upload_avatar(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == "POST":
        profile.avatar = request.FILES.get("avatar")
        profile.save()
        messages.success(request, "Avatar uploaded successfully")
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/accounts/basic-login/")
def change_password(request):
    user = request.user
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if new_password == confirm_new_password:
            if check_password(request.POST.get("current_password"), user.password):
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully")
            else:
                messages.error(request, "Old password doesn't match!")
        else:
            messages.error(request, "Password doesn't match!")

    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="/accounts/basic-login/")
def change_mode(request):
    profile = get_object_or_404(Profile, user=request.user)
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required
def create_user(request):
    if not (request.company and request.user.profile.role == "admin"):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = TenantUserCreationForm(request.POST, company=request.company)
        if form.is_valid():
            form.save(company=request.company)
            messages.success(request, "User created successfully")
            return redirect("user_profile")
    else:
        form = TenantUserCreationForm(company=request.company)

    context = {"form": form, "segment": "new_user", "parent": "team"}
    return render(request, "pages/team/new-user.html", context)


@login_required
def invite_user(request):
    if not (request.company and request.user.profile.role == "admin"):
        return HttpResponseForbidden()

    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            role = form.cleaned_data["role"]
            token = signer.sign(f"{email}|{request.company.id}|{role}")
            invite_link = request.build_absolute_uri(
                reverse("accept_invite", args=[token])
            )
            # In a real app we would send the email here
            messages.success(request, f"Invitation link: {invite_link}")
            return redirect("invite_user")
    else:
        form = InviteUserForm()

    context = {"form": form, "segment": "invite_user", "parent": "apps"}
    return render(request, "users/invite_user.html", context)


def accept_invite(request, token):
    try:
        value = signer.unsign(token, max_age=60 * 60 * 24 * 3)
        email, company_id, role = value.split("|")
    except (BadSignature, SignatureExpired, ValueError):
        raise Http404("Invalid invitation")

    company = get_object_or_404(Company, id=company_id)

    if request.method == "POST":
        form = TenantUserCreationForm(request.POST, initial={"email": email}, company=company)
        if form.is_valid():
            user = form.save(company=company)
            user.email = email
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully")
            return redirect("user_profile")
    else:
        form = TenantUserCreationForm(initial={"email": email, "role": role}, company=company)

    context = {"form": form, "segment": "accept_invite"}
    return render(request, "users/accept_invite.html", context)

