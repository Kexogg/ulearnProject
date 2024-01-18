from django.contrib import admin
from django import forms
from ulearnProject import models


class VacancyForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=models.Skill.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple("Skills", is_stacked=False),
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