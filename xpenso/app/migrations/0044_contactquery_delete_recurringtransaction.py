# Generated by Django 5.1.7 on 2025-04-12 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_customuser_theme_preference'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='RecurringTransaction',
        ),
    ]
