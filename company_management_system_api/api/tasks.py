from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Count
from .models import Office, User, Vehicle
from .constants import ROLE_ADMIN


@shared_task
def email_confirmation_task(code, email, id):
    msg_html = render_to_string('web/email.html',
                                {'code': code, 'link': settings.WEBSITE_URL + f'confirm/{id}'})
    send_mail(
        subject='Email confirmation',
        message=f'Please, confirm your email following by the link {settings.WEBSITE_URL}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.RECIPIENT_ADDRESS, email],
        html_message=msg_html
    )
    print('Success received email!')


@shared_task
def count_vehicle():
    offices = Office.objects.annotate(Count('vehicle'))
    for office in offices:
        if office.vehicle_count != office.vehicle__count:
            office.vehicle_count = office.vehicle__count
            office.save()
    print('Successfully counted')


@shared_task
def send_vehicle_report():
    for admin in User.objects.filter(role=ROLE_ADMIN):
        vehicles = Vehicle.objects.filter(company=admin.company, office__isnull=True)
        msg_html = render_to_string('web/report.html',
                                    {'admin': admin, 'vehicles': vehicles})
        send_mail(
            subject='Weekly vehicle report!',
            message='',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.RECIPIENT_ADDRESS, admin.email],
            html_message=msg_html
        )
    print('Send reports success!')
