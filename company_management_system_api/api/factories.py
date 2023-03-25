import factory
from api.models import User, Office, Company


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = factory.Faker('password')
    is_verified = True


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker('company')
    address = factory.Faker('address')


class OfficeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Office

    name = factory.Faker('name')
    address = factory.Faker('address')
    city = factory.Faker('city')
    country = factory.Faker('country')
    region = factory.Faker('state')
    company = factory.SubFactory(CompanyFactory)
