# Generated by Django 5.1.7 on 2025-04-06 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_alter_budget_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='currency',
        ),
        migrations.AlterField(
            model_name='budget',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
