from django.core.management.base import BaseCommand
from api.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = input('Email: ')
        password = input('Password: ')
        first_name = input('First name: ')
        last_name = input('Last name: ')
        if not email:
            return 'User must have an email'
        if not password:
            return 'User must have an email'
        if not first_name or not last_name:
            return 'User must have first and last names'

        user = User.objects.create(
            email=email, first_name=first_name, last_name=last_name,
            is_staff=True, is_superuser=True, is_active=True
        )
        user.set_password(password)
        user.save()
        return 'Successfully registered!'
