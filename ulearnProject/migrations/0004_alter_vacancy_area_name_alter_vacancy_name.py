# Generated by Django 5.0.1 on 2024-01-20 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ulearnProject', '0003_rename_created_at_vacancy_published_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='area_name',
            field=models.CharField(max_length=200, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название вакансии'),
        ),
    ]
