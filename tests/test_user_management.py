import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from django.core.signing import TimestampSigner
from tests.factories import UserFactory

@pytest.mark.django_db
def test_signup_redirects_to_dashboard(client):
    user = User.objects.create_user(username="admin", password="pass")
    client.login(username="admin", password="pass")
    resp = client.post(reverse("signup_company"), {"company_name": "ACME"})
    assert resp.status_code == 302
    assert "/dashboard/" in resp["Location"]
    user.refresh_from_db()
    assert user.profile.company is not None
    assert user.profile.role == "admin"

@pytest.mark.django_db
def test_invite_user_generates_link(client):
    admin = UserFactory()
    client.login(username=admin.username, password="pass")
    resp = client.post(
        reverse("invite_user"),
        {"email": "new@example.com", "role": "user"},
        follow=True,
    )
    assert resp.status_code == 200
    messages = list(resp.context["messages"])
    assert messages
    assert "accept-invite" in messages[0].message

@pytest.mark.django_db
def test_create_user_creates_profile(client):
    admin = UserFactory()
    client.login(username=admin.username, password="pass")
    resp = client.post(
        reverse("tenant_create_user"),
        {
            "username": "member",
            "email": "member@example.com",
            "password1": "pass1234",
            "password2": "pass1234",
            "role": "user",
        },
    )
    assert resp.status_code == 302
    new_user = User.objects.get(username="member")
    assert new_user.profile.company == admin.profile.company
    assert new_user.profile.role == "user"


@pytest.mark.django_db
def test_accept_invite_creates_user(client):
    admin = UserFactory()
    signer = TimestampSigner()
    token = signer.sign(f"invite@example.com|{admin.profile.company.id}|user")
    resp = client.post(
        reverse("accept_invite", args=[token]),
        {
            "username": "invited",
            "email": "invite@example.com",
            "password1": "pass1234",
            "password2": "pass1234",
            "role": "user",
        },
    )
    assert resp.status_code == 302
    new_user = User.objects.get(username="invited")
    assert new_user.profile.company == admin.profile.company
    assert new_user.profile.role == "user"

@pytest.mark.django_db
def test_profile_update_changes_email_and_position(client):
    user = UserFactory()
    client.login(username=user.username, password="pass")
    resp = client.post(
        reverse("user_profile"),
        {
            "full_name": "Tester",
            "position": "Manager",
            "phone": "111",
            "email": "new@example.com",
        },
        HTTP_REFERER=reverse("user_profile"),
        follow=True,
    )
    assert resp.status_code == 200
    user.refresh_from_db()
    assert user.email == "new@example.com"
    assert user.profile.position == "Manager"

@pytest.mark.django_db
def test_company_users_accessible_for_members(client):
    admin = UserFactory()
    member = UserFactory()
    member.profile.company = admin.profile.company
    member.profile.save()
    client.login(username=member.username, password="pass")
    resp = client.get(reverse("company_users"))
    assert resp.status_code == 200
    assert admin.username in resp.content.decode()
