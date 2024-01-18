from django.shortcuts import render


def demand(request):
    return render(request, 'demand.html', {})