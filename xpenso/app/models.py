from datetime import timedelta
from decimal import Decimal, InvalidOperation
import requests
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils.timezone import now

# --- Currency & Category Choices ---
CURRENCY_CHOICES = [
    ('AUD', 'Australian Dollar'), ('BGN', 'Bulgarian Lev'), ('BRL', 'Brazilian Real'),
    ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc'), ('CNY', 'Chinese Yuan'),
    ('CZK', 'Czech Koruna'), ('DKK', 'Danish Krone'), ('EUR', 'Euro'),
    ('GBP', 'British Pound'), ('HKD', 'Hong Kong Dollar'), ('HRK', 'Croatian Kuna'),
    ('HUF', 'Hungarian Forint'), ('IDR', 'Indonesian Rupiah'), ('ILS', 'Israeli New Shekel'),
    ('INR', 'Indian Rupee'), ('ISK', 'Icelandic Krona'), ('JPY', 'Japanese Yen'),
    ('KRW', 'South Korean Won'), ('MXN', 'Mexican Peso'), ('MYR', 'Malaysian Ringgit'),
    ('NOK', 'Norwegian Krone'), ('NZD', 'New Zealand Dollar'), ('PHP', 'Philippine Peso'),
    ('PLN', 'Polish Zloty'), ('RON', 'Romanian Leu'), ('RUB', 'Russian Ruble'),
    ('SEK', 'Swedish Krona'), ('SGD', 'Singapore Dollar'), ('THB', 'Thai Baht'),
    ('TRY', 'Turkish Lira'), ('USD', 'US Dollar'), ('ZAR', 'South African Rand'),
]

CATEGORY_CHOICES = [
    ('Salary', 'Salary'), ('Freelance', 'Freelance'), ('Investment', 'Investment'),
    ('Other Income', 'Other Income'), ('Food', 'Food'), ('Transport', 'Transport'),
    ('Shopping', 'Shopping'), ('Health', 'Health'), ('Entertainment', 'Entertainment'),
    ('Travel', 'Travel'), ('Education', 'Education'), ('Utilities', 'Utilities'),
    ('Rent', 'Rent'), ('Insurance', 'Insurance'), ('Other Expense', 'Other Expense'),
]

THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]

# --- Custom User Model ---
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# --- Global Currency API Config ---
API_KEY = 'fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o'
API_URL = f'https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}'

# --- Transaction Model ---
class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('Income', 'Income'), ('Expense', 'Expense')])
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    original_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    original_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    conversion_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    date = models.DateTimeField(default=now)
    description = models.TextField(blank=True, null=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.original_currency != self.user.currency:
            self.convert_currency()
        super().save(*args, **kwargs)

    def convert_currency(self):
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            rates = data.get('data', {})

            if self.original_currency in rates and self.user.currency in rates:
                from_rate = Decimal(rates[self.original_currency])
                to_rate = Decimal(rates[self.user.currency])
                self.conversion_rate = to_rate / from_rate
                self.amount = self.original_amount * self.conversion_rate
        except (requests.exceptions.RequestException, KeyError, InvalidOperation) as e:
            print(f"Currency conversion error: {e}")

    def __str__(self):
        return f"{self.type} - {self.amount} {self.user.currency}"


class Budget(models.Model):
    TIME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    time_period = models.CharField(max_length=10, choices=TIME_CHOICES, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.time_period} - {self.amount}"


FREQUENCY_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query from {self.name} ({self.email})"