# Generated by Django 2.2.5 on 2019-10-19 10:33

import Application.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0004_client_late_fee_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Date_Formats',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('Types', models.CharField(choices=[(Application.models.choice('dd:mm:yyyy'), 'dd:mm:yyyy'), (Application.models.choice('mm:dd:yyyy'), 'mm:dd:yyyy')], max_length=10)),
            ],
        ),
    ]