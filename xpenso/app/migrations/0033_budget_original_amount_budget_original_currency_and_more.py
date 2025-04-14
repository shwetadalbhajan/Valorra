# Generated by Django 5.1.7 on 2025-04-07 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_alter_budget_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='original_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AddField(
            model_name='budget',
            name='original_currency',
            field=models.CharField(choices=[('AUD', 'Australian Dollar'), ('BGN', 'Bulgarian Lev'), ('BRL', 'Brazilian Real'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'), ('CNY', 'Chinese Yuan'), ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'), ('GBP', 'British Pound'), ('HKD', 'Hong Kong Dollar'), ('HRK', 'Croatian Kuna'), ('HUF', 'Hungarian Forint'), ('IDR', 'Indonesian Rupiah'), ('ILS', 'Israeli New Shekel'), ('INR', 'Indian Rupee'), ('ISK', 'Icelandic Krona'), ('JPY', 'Japanese Yen'), ('KRW', 'South Korean Won'), ('MXN', 'Mexican Peso'), ('MYR', 'Malaysian Ringgit'), ('NOK', 'Norwegian Krone'), ('NZD', 'New Zealand Dollar'), ('PHP', 'Philippine Peso'), ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'), ('SEK', 'Swedish Krona'), ('SGD', 'Singapore Dollar'), ('THB', 'Thai Baht'), ('TRY', 'Turkish Lira'), ('USD', 'US Dollar'), ('ZAR', 'South African Rand')], default='USD', max_length=3),
        ),
        migrations.AlterField(
            model_name='budget',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Stored in USD', max_digits=12),
        ),
    ]
