from faker import Faker
from rest_framework import status
from django.urls import include, path, reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase, URLPatternsTestCase
from django.test import TestCase
from api.serializers import LoginSerializer, VehicleSerializer
from api.models import User, Company
from api.constants import ROLE_ADMIN, ROLE_REGULAR
from api.constants import OFFICE_EXISTS_ERROR
from .factories import UserFactory, OfficeFactory, CompanyFactory
from rest_framework.authtoken.models import Token


fake = Faker()


class RegistrationTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    def test_success_create_worker_admin(self):
        password = fake.password()
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': password,
            'repeat_password': password,
            'company_name': fake.company()
        }
        response = self.client.post(reverse('sign-up'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().role, ROLE_ADMIN)
        self.assertEqual(Company.objects.count(), 1)

    def test_fail_email_must_be_unique(self):
        user = UserFactory()
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': user.email,
            'password': fake.password(),
            'repeat_password': fake.password(),
            'company_name': fake.company()
        }
        response = self.client.post(reverse('sign-up'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['email'][0], 'This field must be unique.')

    def test_fail_invalid_password_confirm(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': fake.password(),
            'repeat_password': fake.password(),
            'company_name': fake.company()
        }
        response = self.client.post(reverse('sign-up'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['non_field_errors'][0], 'Invalid password confirmation')

    def test_fail_field_is_required(self):
        response = self.client.post(reverse('sign-up'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['first_name'][0], 'This field is required.')
        self.assertEqual(response.json()['last_name'][0], 'This field is required.')
        self.assertEqual(response.json()['email'][0], 'This field is required.')
        self.assertEqual(response.json()['password'][0], 'This field is required.')


class LoginTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    def test_success_login(self):
        user = UserFactory()
        data = {
            'email': user.email,
            'password': user.password
        }
        response = self.client.post(reverse('sign-in'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(response.json().get('auth_token'), Token.objects.first().key)

    def test_invalid_email_or_password(self):
        user = UserFactory()
        data = {
            'email': user.email,
            'password': fake.password()
        }
        response = self.client.post(reverse('sign-in'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors')[0], 'Invalid email or password')


class ModelTestCases(TestCase):
    def test_names_saves_in_upper_case(self):
        user = UserFactory(
            first_name=fake.first_name().lower(),
            last_name=fake.last_name().lower()
        )
        self.assertTrue(user.first_name[0].isupper())
        self.assertTrue(user.last_name[0].isupper())


class SerializerTestCases(TestCase):
    def test_user_is_not_verified(self):
        user = UserFactory(is_verified=False)
        data = {
            'email': user.email,
            'password': user.password
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, 'User is not verified'):
            serializer.is_valid(raise_exception=True)

    def test_can_not_assign_vehicle(self):
        office = OfficeFactory()
        second_office = OfficeFactory()
        user = UserFactory(office=second_office)
        data = {
            'licence_plate': fake.random_digit(),
            'name': fake.name(),
            'model': fake.random_digit(),
            'year_of_manufacture': fake.year(),
            'office': office.id,
            'user': user.id
        }
        serializer = VehicleSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, 'The worker must be from the same office as the vehicle'):
            serializer.is_valid(raise_exception=True)

    def test_office_does_not_exists(self):
        office = OfficeFactory()
        user = UserFactory()
        data = {
            'licence_plate': fake.random_digit(),
            'name': fake.name(),
            'model': fake.random_digit(),
            'year_of_manufacture': fake.year(),
            'office': office.id,
            'user': user.id
        }
        serializer = VehicleSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, OFFICE_EXISTS_ERROR):
            serializer.is_valid(raise_exception=True)


class WorkersAPIView(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('api/', include('api.urls')),
    ]

    def test_create_worker(self):
        company = CompanyFactory()
        user = UserFactory(role=ROLE_ADMIN, company=company)
        token = self.login_user(user)
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': fake.password(),
        }
        response = self.client.post(reverse('worker-list-create'), data, HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(id=response.json()['id']).exists())
        self.assertEqual(response.json()['company']['id'], company.id)

    def test_fail_unauthorized(self):
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': fake.password(),
        }
        response = self.client.post(reverse('worker-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_get_workers(self):
        company = CompanyFactory()
        admin = UserFactory(role=ROLE_ADMIN, company=company)
        UserFactory(role=ROLE_REGULAR, company=company)
        UserFactory(role=ROLE_REGULAR, company=company)
        token = self.login_user(admin)
        response = self.client.get(reverse('worker-list-create'), HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)

    def test_fail_worker_already_exists(self):
        company = CompanyFactory()
        user = UserFactory(role=ROLE_ADMIN, company=company)
        token = self.login_user(user)
        data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': user.email,
            'password': fake.password(),
        }
        response = self.client.post(reverse('worker-list-create'), data, HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['email'][0], 'Worker with this email already exists!')

    def login_user(self, user):
        data = {
            'email': user.email,
            'password': user.password,
        }
        response = self.client.post(reverse('sign-in'), data)
        return response.json().get('auth_token')
