from django.shortcuts import render

from ulearnProject.models import Vacancy


def latest(request):
    vacancies = Vacancy.objects.order_by('created_at')[:5].all()
    print(vacancies)
    return render(request, 'latest.html', {"vacancies": vacancies})
