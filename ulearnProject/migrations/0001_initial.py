# Generated by Django 5.0.1 on 2024-01-18 14:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навыки',
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название вакансии')),
                ('area_name', models.CharField(max_length=100, verbose_name='Город')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('salary_from', models.DecimalField(decimal_places=0, max_digits=10, null=True, verbose_name='Зарплата от')),
                ('salary_to', models.DecimalField(decimal_places=0, max_digits=10, null=True, verbose_name='Зарплата до')),
                ('salary_currency', models.CharField(max_length=3, null=True, verbose_name='Валюта')),
            ],
            options={
                'verbose_name': 'Вакансия',
                'verbose_name_plural': 'Вакансии',
            },
        ),
        migrations.CreateModel(
            name='VacancySkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ulearnProject.skill')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ulearnProject.vacancy')),
            ],
        ),
        migrations.AddField(
            model_name='vacancy',
            name='skills',
            field=models.ManyToManyField(through='ulearnProject.VacancySkill', to='ulearnProject.skill'),
        ),
    ]