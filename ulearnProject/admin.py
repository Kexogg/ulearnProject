from django.contrib import admin
from ulearnProject import models

admin.site.register(models.Vacancy)
admin.site.register(models.Skill)
admin.site.register(models.VacancySkill)