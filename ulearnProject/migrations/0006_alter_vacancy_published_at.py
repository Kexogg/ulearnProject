# Generated by Django 5.0.1 on 2024-01-20 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ulearnProject', '0005_alter_vacancy_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='published_at',
            field=models.DateTimeField(verbose_name='Дата публикации'),
        ),
    ]
