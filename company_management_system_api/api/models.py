import datetime
import random
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from .constants import ROLE_ADMIN, ROLE_REGULAR


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'(id: {self.id}, name: {self.name})'

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class Office(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    vehicle_count = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f'(id: {self.id},' \
               f' name: {self.name},' \
               f' address: {self.address},' \
               f' city: {self.city},' \
               f' region: {self.region})'


class User(AbstractUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.PositiveSmallIntegerField(
        choices=(
            (ROLE_REGULAR, 'Regular'),
            (ROLE_ADMIN, 'Admin')
        ),
        default=ROLE_REGULAR
    )
    username = None
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=True, null=True
    )
    office = models.ForeignKey(
        Office, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return f'(id: {self.id},' \
               f' first_name: {self.first_name},' \
               f' last_name: {self.last_name},' \
               f' role: {self.role},' \
               f' email: {self.email})'

    def is_admin_role(self):
        return self.role == ROLE_ADMIN

    def is_office_exists(self):
        return bool(self.office)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        return super(User, self).save(*args, **kwargs)


class VerificationCode(models.Model):
    code = models.PositiveSmallIntegerField(unique=True, blank=True, null=True)
    code_expiration_date = models.DateTimeField(blank=True, null=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def set_exp_date(self):
        self.code_expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=15)
        return self

    def set_code(self):
        self.code = random.randrange(1111, 9999)
        return self


class Vehicle(models.Model):
    name = models.CharField(max_length=255)
    licence_plate = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year_of_manufacture = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    office = models.ForeignKey(
        Office, on_delete=models.CASCADE, blank=True, null=True
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return f'(id: {self.id},' \
               f' name: {self.name},' \
               f' licence_plate: {self.licence_plate},' \
               f' model: {self.model},' \
               f' year_of_manufacture: {self.year_of_manufacture})'
