from functools import lru_cache

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
    i = np.arange(len(vacancies))
    values_list = vacancies.values_list('year', 'count', 'count_fullstack', 'avg_salary', 'avg_salary_fullstack')
    years, counts, counts_fullstack, avg_salaries, avg_salaries_fullstack = zip(*values_list)
    axs[0].bar(i + width / 2, counts, width, label='Все вакансии')
    axs[0].bar(i - width / 2, counts_fullstack, width, label='Fullstack вакансии')
    axs[0].set_xticks(i + width / 2)
    axs[0].set_xticklabels(years, rotation=45)
    axs[0].legend(fontsize=12)
    axs[0].set_ylabel('Количество вакансий')
    axs[0].set_title('Вакансии по годам')

    axs[1].bar(i + width / 2, avg_salaries, width, label='Все вакансии')
    axs[1].bar(i - width / 2, avg_salaries_fullstack, width, label='Fullstack вакансии')
    axs[1].set_xticks(i + width / 2)
    axs[1].set_xticklabels(years, rotation=45)
    axs[1].legend(fontsize=12, loc='upper left')
    axs[1].set_ylabel('Средняя зарплата')
    axs[1].set_title('Средняя зарплата по годам')
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


@lru_cache(maxsize=None)
def get_data():
    years = Vacancy.objects.annotate(
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
                    Q(name__icontains='фулстэк') |
                    Q(name__icontains='full stack'),
                    then='salary'
                ),
                default=None,
                output_field=IntegerField()
            )
        ),
    ).exclude(salary__gt=10000000).order_by('year')
    return years


@cache_page(60 * 60 * 24)
def demand(request):
    years = get_data()
    # return render(request, 'demand.html', {'graph': graph, 'vacancies': vacancies})
    content = [
        {'year': year['year'], 'count': year['count'],
         'fraction_fullstack': str(round(year['count_fullstack'] / year['count'] * 100, 2)) + '%',
         'avg_salary':  round(year['avg_salary'], 2),
         'avg_salary_fullstack': round(year['avg_salary_fullstack'], 2) if year['avg_salary_fullstack'] else None,
         'count_fullstack': year['count_fullstack'],
         } for year in years
    ]
    return render(request, 'stats.html',
                  {
                      "title": "Востребованность",
                      "accordions":
                          {
                              "Статистика востребованности вакансий Fullstack относительно всех вакансий":
                                  [
                                      {
                                          'title': 'Таблица',
                                          'columns': {'year': 'Год', 'count': 'Количество',
                                                      'avg_salary': 'Средняя зарплата (₽)',
                                                      'count_fullstack': 'Количество Fullstack',
                                                      'fraction_fullstack': 'Доля Fullstack',
                                                      'avg_salary_fullstack': 'Средняя зарплата Fullstack (₽)'},
                                          'type': 'table',
                                          'content': content
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(years)
                                      },
                                  ],
                          }
                  })
