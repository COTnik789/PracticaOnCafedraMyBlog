# Generated by Django 5.2.4 on 2025-07-14 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_notification',
            field=models.BooleanField(default=True, help_text='Получать уведомления по email'),
        ),
        migrations.AddField(
            model_name='profile',
            name='theme_preference',
            field=models.CharField(choices=[('light', 'Светлая'), ('dark', 'Тёмная')], default='light', max_length=20),
        ),
    ]
