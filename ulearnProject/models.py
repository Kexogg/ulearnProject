from django.db import models


class Skill(models.Model):
    name = models.CharField('Название навыка', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    name = models.CharField('Название вакансии', max_length=500)
    area_name = models.CharField('Город', max_length=200)
    published_at = models.DateTimeField('Дата публикации')
    salary = models.DecimalField('Зарплата', max_digits=10, decimal_places=0, null=True)
    skills = models.ManyToManyField("Skill", through="VacancySkill")

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return f'{self.name}, {self.area_name}'


class VacancySkill(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
