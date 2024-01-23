from django.db import models
from ckeditor.fields import RichTextField

class Skill(models.Model):
    name = models.CharField('Название навыка', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    name = models.CharField('Название вакансии', max_length=500)
    area_name = models.CharField('Город', max_length=200, null=True)
    published_at = models.DateTimeField('Дата публикации', null=True)
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


class GeographyStats(models.Model):
    area_name = models.CharField('Город', max_length=200, unique=True)
    count = models.IntegerField('Количество вакансий')
    count_fullstack = models.IntegerField('Количество вакансий fullstack')
    average_salary = models.DecimalField('Средняя зарплата', max_digits=10, decimal_places=0)
    average_salary_fullstack = models.DecimalField('Средняя зарплата fullstack', max_digits=10, decimal_places=0,
                                                   null=True)
    fraction = models.DecimalField('Доля вакансий', max_digits=10, decimal_places=4)
    fraction_fullstack = models.DecimalField('Доля вакансий fullstack', max_digits=10, decimal_places=4, null=True)

    class Meta:
        verbose_name = 'Статистика по регионам'
        verbose_name_plural = 'Статистика по регионам'

    def __str__(self):
        return f'{self.area_name}, {self.count}'


class DemandStats(models.Model):
    year = models.IntegerField('Год', unique=True)
    count = models.IntegerField('Количество вакансий')
    count_fullstack = models.IntegerField('Количество вакансий fullstack', null=True)
    average_salary = models.DecimalField('Средняя зарплата', max_digits=10, decimal_places=0)
    average_salary_fullstack = models.DecimalField('Средняя зарплата fullstack', max_digits=10, decimal_places=0,
                                                   null=True)
    fraction_fullstack = models.DecimalField('Доля вакансий fullstack', max_digits=10, decimal_places=0, null=True)

    class Meta:
        verbose_name = 'Статистика по востребованности'
        verbose_name_plural = 'Статистика по востребованности'

    def __str__(self):
        return f'{self.year}'


class SkillStats(models.Model):
    year = models.IntegerField('Год')
    skill = models.CharField('Навык', max_length=100)
    count = models.IntegerField('Количество вакансий')
    fraction = models.DecimalField('Доля вакансий с навыком', max_digits=10, decimal_places=2)
    isFullstack = models.BooleanField('Fullstack')
    average_salary = models.DecimalField('Средняя зарплата', max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = 'Статистика по навыкам'
        verbose_name_plural = 'Статистика по навыкам'

    def __str__(self):
        return f'{self.skill}, {self.count}, {self.isFullstack}, {self.year}'


class Page(models.Model):
    name = models.CharField('Название страницы', max_length=100, unique=True)
    path = models.CharField('Путь', max_length=100, unique=True)
    content = RichTextField('Содержимое страницы')
    
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.name
