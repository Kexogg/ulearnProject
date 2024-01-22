from functools import lru_cache

import matplotlib.pyplot as plt
from io import StringIO

import numpy as np
from django.db.models import Q
from django.shortcuts import render
from django.db import models
from django.views.decorators.cache import cache_page
from ulearnProject.models import Vacancy


@lru_cache(maxsize=None)
def get_graph(vacancies):
    width = 0.35
    fig, axs = plt.subplots(2)
    fig.set_figwidth(10)
    fig.set_figheight(10)
    fig.subplots_adjust(hspace=0.5)
    # fig.subplots_adjust(wspace=0.5)
    i = np.arange(10)
    avg_salary, area_name = zip(
        *vacancies.values_list('avg_salary', 'area_name').exclude(salary__isnull=True).exclude(
            fraction__lt=0.5).order_by('-avg_salary')[:10])

    axs[0].barh(i + width / 2, avg_salary, width)
    axs[0].set_yticks(i + width / 2)
    axs[0].invert_yaxis()
    axs[0].set_yticklabels(area_name)
    axs[0].set_xlabel('Зарплата')
    axs[0].tick_params(axis='y', labelsize=8)
    for tick in axs[0].get_xticklabels():
        tick.set_rotation(45)
    axs[0].set_title('Средняя зарплата по регионам')

    fraction, area_name = zip(*vacancies.values_list('fraction', 'area_name').order_by('-fraction')[:9])
    fraction = list(fraction)
    fraction.append(100 - sum(fraction))
    area_name = list(area_name)
    area_name.append('Другие')

    axs[1].pie(fraction, labels=area_name)
    axs[1].set_title('Доля регионов')

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


@lru_cache(maxsize=None)
def get_data():
    vacancies_fullstack = Vacancy.objects.filter(
        Q(name__icontains='fullstack') |
        Q(name__icontains='фулстак') |
        Q(name__icontains='фуллтак') |
        Q(name__icontains='фуллстэк') |
        Q(name__icontains='фулстэк') |
        Q(name__icontains='full stack')
    )
    vacancies_fullstack = vacancies_fullstack.values('area_name').annotate(
        count=models.Count('id'),
        fraction=(models.Count('id') / float(vacancies_fullstack.count())) * 100,
        avg_salary=models.Avg('salary', output_field=models.IntegerField()),
    ).exclude(salary__gt=10000000)

    vacancies = Vacancy.objects.values('area_name').annotate(
        count=models.Count('id'),
        fraction=(models.Count('id') / float(Vacancy.objects.count())) * 100,
        avg_salary=models.Avg('salary', output_field=models.IntegerField())
    ).exclude(salary__gt=10000000)

    return vacancies, vacancies_fullstack


@cache_page(60 * 60 * 24)
def geography(request):
    regions, regions_fullstack = get_data()
    content1 = [
        {'area_name': region['area_name'], 'count': region['count'],
         'fraction': str(round(region['fraction'], 2)) + '%',
         'avg_salary': region['avg_salary']} for region in regions.order_by('-fraction')[:10]
    ]
    content2 = [
        {'area_name': region['area_name'], 'count': region['count'],
         'fraction': str(round(region['fraction'], 2)) + '%',
         'avg_salary': region['avg_salary']} for region in regions_fullstack.order_by('-fraction')[:10]
    ]
    return render(request, 'stats.html',
                  {
                      "accordions":
                          {
                              "Общая география вакансий":
                                  [
                                      {
                                          'title': 'Таблица',
                                          'columns': {'area_name': 'Регион', 'count': 'Количество', 'fraction': 'Доля',
                                                      'avg_salary': 'Средняя зарплата'},
                                          'type': 'table',
                                          'content': content1
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(regions)
                                      },
                                  ],
                              "География вакансий Fullstack":
                                  [
                                      {
                                          'title': 'Таблица',
                                          'columns': {'area_name': 'Регион', 'count': 'Количество', 'fraction': 'Доля',
                                                      'avg_salary': 'Средняя зарплата'},
                                          'type': 'table',
                                          'content': content2
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(regions_fullstack)
                                      },
                                  ]
                          }
                  })
