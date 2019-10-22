# Generated by Django 3.0a1 on 2019-10-21 21:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('Account_Id', models.AutoField(primary_key=True, serialize=False)),
                ('Tax', models.FloatField()),
                ('Tax_type', models.CharField(max_length=20)),
                ('Currency', models.CharField(max_length=5)),
                ('Late_Fees', models.FloatField()),
                ('Due_Date', models.DateField()),
                ('Due_Amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('Client_Id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('Fname', models.CharField(max_length=50)),
                ('Lname', models.CharField(max_length=50)),
                ('Address_Line', models.TextField()),
                ('City', models.CharField(max_length=30)),
                ('Pin_Code', models.PositiveSmallIntegerField()),
                ('State', models.CharField(max_length=30)),
                ('Late_Fee_Rate', models.FloatField(default=0)),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('Company_Id', models.AutoField(primary_key=True, serialize=False)),
                ('Company_Name', models.CharField(max_length=50)),
                ('Address_Line', models.TextField()),
                ('City', models.CharField(max_length=30)),
                ('Pin_Code', models.PositiveSmallIntegerField(default=0)),
                ('State', models.CharField(max_length=30)),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.PositiveSmallIntegerField()),
                ('Date', models.DateField()),
                ('Tax_Rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('Country_Code', models.CharField(max_length=10)),
                ('Country_Name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('Code', models.CharField(max_length=10)),
                ('Name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneCode',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('Country_Name', models.CharField(max_length=50)),
                ('ISO_Code', models.CharField(max_length=10)),
                ('ISD_Code', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Quotes',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False)),
                ('AFName', models.CharField(max_length=20)),
                ('ALName', models.CharField(max_length=20)),
                ('Quote', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('Vendor_Id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('Vendor_Name', models.CharField(max_length=100)),
                ('Vendor_Category', models.CharField(max_length=10)),
                ('Address_Line', models.TextField()),
                ('City', models.CharField(max_length=30)),
                ('Pin_Code', models.PositiveSmallIntegerField()),
                ('State', models.CharField(max_length=30)),
                ('Email', models.EmailField(max_length=254)),
                ('Phone', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Vendor_Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Account_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Account')),
                ('Vendor_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Vendor')),
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
                ('Pin_Code', models.PositiveSmallIntegerField(default=0)),
                ('State', models.CharField(max_length=30)),
                ('Email', models.EmailField(max_length=254)),
                ('Password', models.CharField(default='', max_length=100)),
                ('Phone', models.PositiveSmallIntegerField()),
                ('Auth_Level', models.PositiveSmallIntegerField()),
                ('Comp_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('Transaction_Id', models.AutoField(primary_key=True, serialize=False)),
                ('Transaction_Date', models.DateField()),
                ('Transaction_amt', models.FloatField()),
                ('Account_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Account')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='Base_Currency',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='Application.Currency'),
        ),
        migrations.CreateModel(
            name='Client_Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Account_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Account')),
                ('Client_Id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Application.Client')),
            ],
        ),
    ]
