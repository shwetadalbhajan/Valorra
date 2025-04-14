# Generated by Django 5.1.7 on 2025-04-07 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_rename_period_budget_budget_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='amount',
            field=models.FloatField(help_text='Stored in base currency (USD)'),
        ),
    ]
