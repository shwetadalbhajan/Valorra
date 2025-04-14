# Generated by Django 5.1.7 on 2025-04-03 06:28

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_recurringtransaction_original_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='category',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='converted_amount',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='frequency',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='next_occurrence',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='original_amount',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='original_currency',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='type',
        ),
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='user',
        ),
        migrations.AlterField(
            model_name='budget',
            name='converted_daily_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='converted_monthly_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='converted_weekly_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='original_daily_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='original_monthly_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='original_weekly_budget',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12, null=True),
        ),
    ]
