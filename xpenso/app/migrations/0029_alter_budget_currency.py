# Generated by Django 5.1.7 on 2025-04-03 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_budget_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='currency',
            field=models.CharField(default='USD', max_length=3),
        ),
    ]
