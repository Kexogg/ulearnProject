from django.contrib import admin
from django import forms
from django.urls import path

from ulearnProject import models
from ulearnProject.views.import_csv import import_csv


class VacancyForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=models.Skill.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("skills", is_stacked=False),
        required=False,
        label=''
    )

    class Meta:
        model = models.Vacancy
        fields = '__all__'


class VacancyAdmin(admin.ModelAdmin):
    form = VacancyForm


admin.site.register(models.Vacancy, VacancyAdmin)
admin.site.register(models.Skill)

admin.site.register(models.GeographyStats)
admin.site.register(models.DemandStats)
admin.site.register(models.SkillStats)


urlpatterns = [
    path('admin/import_csv/', import_csv, name='import_csv'),
]