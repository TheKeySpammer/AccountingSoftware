# Generated by Django 3.0a1 on 2019-10-14 22:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('Company_Id', models.AutoField(primary_key=True, serialize=False)),
                ('Company_Name', models.CharField(max_length=50)),
                ('Address_Line', models.TextField()),
                ('City', models.CharField(max_length=30)),
                ('State', models.CharField(max_length=30)),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.PositiveSmallIntegerField()),
                ('Date', models.DateField()),
                ('Tax_Rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('User_Id', models.AutoField(primary_key=True, serialize=False)),
                ('Fname', models.CharField(max_length=50)),
                ('Lname', models.CharField(max_length=50)),
                ('Address_Line', models.TextField()),
                ('City', models.CharField(max_length=30)),
                ('State', models.CharField(max_length=30)),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.PositiveSmallIntegerField()),
                ('Auth_Level', models.PositiveSmallIntegerField()),
                ('Comp_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Company')),
            ],
        ),
    ]