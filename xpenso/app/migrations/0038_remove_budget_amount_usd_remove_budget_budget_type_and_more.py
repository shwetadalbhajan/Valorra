# Generated by Django 5.1.7 on 2025-04-07 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_budget'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='amount_usd',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_type',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='conversion_rate',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='original_amount',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='original_currency',
        ),
        migrations.AddField(
            model_name='budget',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='budget',
            name='time_period',
            field=models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default=None, max_length=10),
        ),
    ]
