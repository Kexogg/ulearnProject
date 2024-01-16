from django.core.exceptions import ValidationError
from django.db import models
import hashlib


class Vacancy(models.Model):
    name = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=0)
    area_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vacancy'

    @property
    def skills(self):
        return [item.skill.name for item in self.vacancyskill_set.all()]


class Skill(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'skill'


class VacancySkill(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vacancy_skill'
        unique_together = ('vacancy', 'skill')
