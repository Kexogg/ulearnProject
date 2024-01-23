import math
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from ulearnProject.models import SkillStats


def get_graph(skills):
    width = 0.35
    sqrt_len_skills = math.sqrt(skills.values('year').distinct().count())
    if sqrt_len_skills.is_integer():
        rows = cols = int(sqrt_len_skills)
    else:
        rows = int(sqrt_len_skills)
        cols = rows + 1
    fig, axs = plt.subplots(rows, cols)
    fig.set_figwidth(15)
    fig.set_figheight(15)
    fig.subplots_adjust(hspace=0.5)
    fig.subplots_adjust(wspace=0.5)
    fig.suptitle('Востребованность навыков', fontsize=24)
    years = skills.values_list('year', flat=True).distinct()
    for i, year in enumerate(years):
        x = np.arange(skills.filter(year=year).count())
        y = np.array(skills.filter(year=year).values_list('count', flat=True))
        axs[i // cols, i % cols].bar(x, y, width)
        axs[i // cols, i % cols].set_title(year)
        axs[i // cols, i % cols].set_xticks(x)
        axs[i // cols, i % cols].set_xticklabels(skills.filter(year=year).values_list('skill', flat=True),
                                                 rotation=90)
        axs[i // cols, i % cols].set_ylabel('Упоминания')
        axs[i // cols, i % cols].set_xlabel('Навык')
        axs[i // cols, i % cols].set_ylim([0, max(y) * 1.2])
        axs[i // cols, i % cols].grid(True)
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    data = imgdata.getvalue()
    return data


def get_data():
    return SkillStats.objects.all()


@cache_page(60 * 60 * 24)
def skills(request):
    skills = get_data()
    years = skills.values_list('year', flat=True).distinct()
    content_all = {}
    content_fullstack = {}
    for year in years:
        content_all[year] = [{'skill': skill['skill'], 'count': skill['count']} for skill in
                             skills.filter(year=year, isFullstack=False).values('skill', 'count')]
        content_fullstack[year] = [{'skill': skill['skill'], 'count': skill['count']} for skill in
                                   skills.filter(year=year, isFullstack=True).values('skill', 'count')]
    return render(request, 'stats.html',
                  {
                      "title": "Востребованность навыков",
                      "accordions":
                          {
                              "Топ-20 навыков по годам":
                                  [
                                      {
                                          'title': 'Таблицы',
                                          'columns': {'skill': 'Навык', 'count': 'Количество'},
                                          'type': 'table_grid',
                                          'content': content_all
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills.filter(isFullstack=False))
                                      },
                                  ],
                              "Топ-20 навыков FullStack-вакансий по годам":
                                  [
                                      {
                                          'title': 'Таблицы',
                                          'columns': {'skill': 'Навык', 'count': 'Количество'},
                                          'type': 'table_grid',
                                          'content': content_fullstack
                                      },
                                      {
                                          'title': 'График',
                                          'type': 'chart',
                                          'content': get_graph(skills.filter(isFullstack=True))
                                      },
                                  ]
                          }
                  })
