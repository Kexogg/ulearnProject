import matplotlib.pyplot as plt
from io import StringIO

import numpy as np
from django.db.models.functions import ExtractYear
from django.db.models import Q, Avg, Case, When, IntegerField, FloatField, DecimalField
from django.shortcuts import render
from django.db import models
from django.views.decorators.cache import cache_page

from ulearnProject.models import Vacancy


def get_graph(vacancies):
    width = 0.35

    fig, axs = plt.subplots(2)
    fig.subplots_adjust(hspace=0.5)
    fig.set_figwidth(10)
    i = np.arange(len(vacancies.values_list('year', flat=True)))
    axs[0].bar(i + width / 2, vacancies.values_list('count', flat=True), width, label='Все вакансии')
    axs[0].bar(i - width / 2, vacancies.values_list('count_fullstack', flat=True), width, label='Fullstack вакансии')
    axs[0].set_xticks(i + width / 2)
    axs[0].set_xticklabels(vacancies.values_list('year', flat=True), rotation=45)
    axs[0].legend(fontsize=12)
    axs[0].set_ylabel('Количество вакансий')
    axs[0].set_title('Вакансии по годам')

    axs[1].bar(i + width / 2, vacancies.values_list('avg_salary', flat=True), width, label='Все вакансии')
    axs[1].bar(i - width / 2, vacancies.values_list('avg_salary_fullstack', flat=True), width,
               label='Fullstack вакансии')
    axs[1].set_xticks(i + width / 2)
    axs[1].set_xticklabels(vacancies.values_list('year', flat=True), rotation=45)
    axs[1].legend(fontsize=12, loc='upper left')
    axs[1].set_ylabel('Средняя зарплата')
    axs[1].set_title('Средняя зарплата по годам')
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    plt.show()
    data = imgdata.getvalue()
    return data


def get_data():
    vacancies = Vacancy.objects.annotate(
        year=ExtractYear('published_at')
    ).values('year').annotate(
        count=models.Count('id'),
        avg_salary=models.Avg('salary', output_field=models.DecimalField()),
        count_fullstack=models.Sum(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then=1
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        avg_salary_fullstack=models.Avg(
            Case(
                When(
                    Q(name__icontains='fullstack') |
                    Q(name__icontains='фулстак') |
                    Q(name__icontains='фуллтак') |
                    Q(name__icontains='фуллстэк') |
                    Q(name__icontains='фулстэk') |
                    Q(name__icontains='full stack'),
                    then='salary'
                ),
                default=None,
                output_field=DecimalField()
            )
        )
    ).exclude(salary__gt=10000000).order_by('year')
    return vacancies


@cache_page(60 * 15)
def demand(request):
    vacancies = get_data()
    graph = get_graph(vacancies)
    return render(request, 'demand.html', {'graph': graph, 'vacancies': vacancies})
