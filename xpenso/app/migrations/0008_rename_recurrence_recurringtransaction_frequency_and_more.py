# Generated by Django 5.1.7 on 2025-03-31 13:01

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_budget_recurringtransaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recurringtransaction',
            old_name='recurrence',
            new_name='frequency',
        ),
        migrations.RenameField(
            model_name='recurringtransaction',
            old_name='transaction_type',
            new_name='type',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_type',
        ),
        migrations.AddField(
            model_name='budget',
            name='daily_budget',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='budget',
            name='monthly_budget',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='budget',
            name='weekly_budget',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AlterField(
            model_name='budget',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='category',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='next_due_date',
            field=models.DateField(),
        ),
    ]
