from django import forms
from django.contrib import admin
from ulearnProject import models


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


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()
