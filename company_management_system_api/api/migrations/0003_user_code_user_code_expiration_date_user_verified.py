# Generated by Django 4.1.2 on 2022-10-27 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='code',
            field=models.PositiveSmallIntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='code_expiration_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]