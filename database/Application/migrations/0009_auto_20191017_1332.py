# Generated by Django 3.0a1 on 2019-10-17 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0008_auto_20191016_0338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonecode',
            name='Country_Name',
            field=models.CharField(max_length=50),
        ),
    ]
