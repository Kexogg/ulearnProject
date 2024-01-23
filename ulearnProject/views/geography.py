import matplotlib.pyplot as plt
from io import StringIO

import numpy as np
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from ulearnProject.models import GeographyStats


def get_graph(stats):
    width = 0.35
    fig, axs = plt.subplots(2)
    fig.set_figwidth(10)
    fig.set_figheight(10)
    fig.subplots_adjust(hspace=0.5)
    i = np.arange(10)

    stats.sort(key=lambda x: x['avg_salary'], reverse=True)
    avg_salary, area_name = (
        zip(*[(region['avg_salary'], region['area_name']) for region in
              stats[:10]]))

    axs[0].barh(i + width / 2, avg_salary, width)
    axs[0].set_yticks(i + width / 2)
    axs[0].invert_yaxis()
    axs[0].set_yticklabels(area_name)
    axs[0].set_xlabel('Зарплата')
    axs[0].tick_params(axis='y', labelsize=8)
    for tick in axs[0].get_xticklabels():
        tick.set_rotation(45)
    axs[0].set_title('Средняя зарплата по регионам')

    stats.sort(key=lambda x: x['fraction'], reverse=True)
    fraction, area_name = (
        zip(*[(region['fraction'], region['area_name']) for region in
              stats[:9]]))

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


def get_data():
    return GeographyStats.objects.all()


@cache_page(60 * 60 * 24)
def geography(request):
    stats = get_data()
    content1 = [
        {'area_name': region.area_name, 'count': region.count,
         'fraction': round(region.fraction, 2),
         'avg_salary': region.average_salary} for region in stats.order_by('-fraction')[:10]
    ]
    content2 = [
        {'area_name': region.area_name, 'count': region.count_fullstack,
         'fraction': round(region.fraction_fullstack, 2),
         'avg_salary': region.average_salary_fullstack} for region in stats.order_by('-fraction_fullstack')[:10]
    ]
    return render(request, 'stats.html',
                  {
                      "title": "География вакансий",
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
                                          'content': get_graph(content1)
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
                                          'content': get_graph(content2)
                                      },
                                  ]
                          }
                  })
