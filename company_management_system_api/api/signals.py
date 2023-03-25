from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, VerificationCode, Vehicle
from .tasks import email_confirmation_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


channel_layer = get_channel_layer()


@receiver(post_save, sender=User)
def email_confirm(sender, instance, created, **kwargs):
    if created:
        user_code = VerificationCode.objects.create(user=instance)
        user_code.set_code()
        user_code.set_exp_date()
        user_code.save()
        email_confirmation_task.delay(user_code.code, instance.email, instance.id)


@receiver(post_save, sender=Vehicle)
def broadcast_report(sender, instance, created, **kwargs):
    if created:
        async_to_sync(channel_layer.group_send)('vehicles', {'type': 'send_vehicle', 'text': instance.name})
