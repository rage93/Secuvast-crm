import factory
from django.contrib.auth.models import User
from apps.companies.models import Company
from apps.users.models import Profile

class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"Co{n}")

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall("set_password", "pass")

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if not create:
            return
        company = kwargs.get("company") or CompanyFactory()
        prof = self.profile  # profile created via signals
        prof.company = company
        prof.role = "admin"
        prof.save()
