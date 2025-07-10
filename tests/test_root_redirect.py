import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_subdomain_redirect(client):
    resp = client.get(reverse('landing'), HTTP_HOST='foo.localhost')
    assert resp.status_code == 302
    assert '//localhost' in resp['Location']
