from tests.factories import CompanyFactory, UserFactory

for i in range(3):
    company = CompanyFactory()
    UserFactory(company=company)
    print(f"Created {company.slug_subdomain}")
