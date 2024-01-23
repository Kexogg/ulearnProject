import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ulearnProject.models import DemandStats, Page


def get_graph(stats):
    width = 0.4
    fig, axs = plt.subplots(2)
    fig.subplots_adjust(hspace=0.5)
    i = np.arange(len(stats))
    years, counts, counts_fullstack, avg_salaries, avg_salaries_fullstack = (
        zip(*[(stat.year, stat.count, stat.count_fullstack, stat.average_salary,
               stat.average_salary_fullstack
               ) for stat in
              stats]))
    axs[0].bar(i, counts, width, label='Все вакансии')
    axs[0].bar(i + width, counts_fullstack, width, label='Fullstack вакансии')
    axs[0].set_xticks(i + width / 2)
    axs[0].set_xticklabels(years, rotation=45)
    axs[0].legend(fontsize=12)
    axs[0].set_ylabel('Количество вакансий')
    axs[0].set_title('Вакансии по годам')
    axs[0].grid(True)

    axs[1].bar(i, avg_salaries, width, label='Все вакансии')
    axs[1].bar(i + width, avg_salaries_fullstack, width, label='Fullstack вакансии')
    axs[1].set_xticks(i + width / 2)
    axs[1].set_xticklabels(years, rotation=45)
    axs[1].legend(fontsize=12, loc='upper left')
    axs[1].set_ylabel('Средняя зарплата')
    axs[1].set_title('Средняя зарплата по годам')
    axs[1].grid(True)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


def get_data():
    return DemandStats.objects.all()


@cache_page(60 * 60 * 24)
def demand(request):
    years = get_data()
    content = [
        {'year': year.year, 'count': year.count,
         'fraction_fullstack': str(round(year.count_fullstack / year.count * 100, 2)) + '%',
         'avg_salary': round(year.average_salary, 2),
         'avg_salary_fullstack': round(year.average_salary_fullstack, 2) if year.average_salary_fullstack else None,
         'count_fullstack': year.count_fullstack,
         } for year in years
    ]
    return render(request, 'stats.html',
                  {
                      "page": Page.objects.get(path='/demand/'),
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
