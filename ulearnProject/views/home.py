from django.shortcuts import render

from ulearnProject.models import Page


def home(request):
    page = Page.objects.get(path='/')
    return render(request, 'home.html', {'page': page})