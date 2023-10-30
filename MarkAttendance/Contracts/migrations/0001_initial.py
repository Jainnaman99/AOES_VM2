# Generated by Django 4.1.5 on 2023-10-19 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('contract_name', models.CharField(max_length=200)),
                ('contract_acronym', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('contract_type', models.CharField(choices=[('T&M Price', 'T&M Price'), ('Fixed Price', 'Fixed Price')], max_length=50)),
                ('FTE_count', models.IntegerField(default=0)),
                ('total_contract_value', models.FloatField()),
                ('revenue_projection', models.FloatField(blank=True, default=0)),
                ('revenue_recognised', models.FloatField(blank=True, default=0)),
                ('total_amount_consumed', models.FloatField(blank=True, default=0, editable=False)),
                ('balance', models.FloatField(blank=True, default=0, editable=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], max_length=50)),
            ],
        ),
    ]
