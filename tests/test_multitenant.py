import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse
from apps.companies.models import Company
from django.core.exceptions import ValidationError

@pytest.mark.django_db
def test_user_cannot_access_other_company(client):
    c1 = Company.objects.create(name="C1", slug_subdomain="c1")
    c2 = Company.objects.create(name="C2", slug_subdomain="c2")
    u1 = User.objects.create_user(username="u1", password="pass")
    u1.profile.company = c1
    u1.profile.role = "admin"
    u1.profile.save()
    client.login(username="u1", password="pass")
    resp = client.get(reverse("company_info"), HTTP_HOST="c2.example.com")
    assert resp.status_code == 403

@pytest.mark.django_db
def test_superuser_access_all_companies(client):
    c = Company.objects.create(name="C", slug_subdomain="c")
    superuser = User.objects.create_superuser("su", "su@example.com", "pass")
    client.login(username="su", password="pass")
    resp = client.get(reverse("company_info"), HTTP_HOST="c.example.com")
    assert resp.status_code == 200

@pytest.mark.django_db
def test_redirect_middleware(client):
    c = Company.objects.create(name="RCo", slug_subdomain="rco")
    u = User.objects.create_user(username="r", password="pass")
    u.profile.company = c
    u.profile.save()
    client.login(username="r", password="pass")
    resp = client.get("/", HTTP_HOST="www.localhost")
    assert resp.status_code == 302
    assert f"//{c.slug_subdomain}.localhost" in resp["Location"]

@pytest.mark.django_db
def test_groups_created_with_permissions(client):
    Company.objects.create(name="GCo", slug_subdomain="gco")
    groups = Group.objects.filter(name__startswith="gco-")
    assert groups.count() == 4
    perms = {g.name.split("-",1)[1]: set(g.permissions.values_list("codename", flat=True)) for g in groups}
    assert "add_user" in perms["Admin"]


@pytest.mark.django_db
def test_reserved_subdomain():
    with pytest.raises(ValidationError):
        Company.objects.create(name="Bad", slug_subdomain="www")


@pytest.mark.django_db
def test_healthz_endpoint(client):
    c = Company.objects.create(name="H", slug_subdomain="h")
    resp = client.get(reverse("company_healthz"), HTTP_HOST="h.example.com")
    assert resp.status_code == 200
    c.life_cycle = Company.LifeCycle.SUSPENDED
    c.save(update_fields=["life_cycle"])
    resp = client.get(reverse("company_healthz"), HTTP_HOST="h.example.com")
    assert resp.status_code == 503


@pytest.mark.django_db
def test_company_row_version():
    c = Company.objects.create(name="Ver", slug_subdomain="ver")
    c1 = Company.objects.get(pk=c.pk)
    c2 = Company.objects.get(pk=c.pk)
    c1.name = "First"
    c1.save()
    c2.name = "Second"
    with pytest.raises(ValidationError):
        c2.save()


@pytest.mark.django_db
def test_sidebar_visible_for_admin(client):
    c = Company.objects.create(name="SCo", slug_subdomain="sco")
    u = User.objects.create_user(username="a", password="pass")
    u.profile.company = c
    u.profile.role = "admin"
    u.profile.save()
    client.login(username="a", password="pass")
    resp = client.get(reverse("index"), HTTP_HOST="sco.example.com")
    assert resp.status_code == 200
    assert b"/company/info/" in resp.content
    assert b"Billing" in resp.content


@pytest.mark.django_db
def test_sidebar_hidden_for_normal_user(client):
    c = Company.objects.create(name="NCo", slug_subdomain="nco")
    u = User.objects.create_user(username="n", password="pass")
    u.profile.company = c
    u.profile.role = "user"
    u.profile.save()
    client.login(username="n", password="pass")
    resp = client.get(reverse("index"), HTTP_HOST="nco.example.com")
    assert resp.status_code == 200
    assert b"/company/info/" not in resp.content


@pytest.mark.django_db
def test_sidebar_hidden_without_company(client):
    u = User.objects.create_user(username="x", password="pass")
    client.login(username="x", password="pass")
    resp = client.get(reverse("landing"), HTTP_HOST="www.example.com")
    assert resp.status_code == 200
    assert b"/company/info/" not in resp.content
