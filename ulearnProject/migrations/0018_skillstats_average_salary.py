# Generated by Django 5.0.1 on 2024-01-23 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ulearnProject', '0017_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillstats',
            name='average_salary',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=10, verbose_name='Средняя зарплата'),
            preserve_default=False,
        ),
    ]