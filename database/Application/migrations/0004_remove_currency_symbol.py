# Generated by Django 3.0a1 on 2019-10-15 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0003_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currency',
            name='Symbol',
        ),
    ]