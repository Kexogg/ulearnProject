# Generated by Django 5.0.1 on 2024-01-18 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ulearnProject', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='description',
            field=models.TextField(null=True, verbose_name='Описание вакансии'),
        ),
    ]
