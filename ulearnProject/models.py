from django.db import models


class Skill(models.Model):
    name = models.CharField('Название навыка', max_length=100)

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    name = models.CharField('Название вакансии', max_length=100)
    area_name = models.CharField('Город', max_length=100)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    salary_from = models.DecimalField('Зарплата от', max_digits=10, decimal_places=0, null=True)
    salary_to = models.DecimalField('Зарплата до', max_digits=10, decimal_places=0, null=True)
    salary_currency = models.CharField('Валюта', max_length=3, null=True)
    description = models.TextField('Описание вакансии', null=True)
    skills = models.ManyToManyField("Skill", through="VacancySkill")

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'


class VacancySkill(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
