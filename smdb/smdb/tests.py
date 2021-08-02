import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_create():
    User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
    assert User.objects.count() == 1
