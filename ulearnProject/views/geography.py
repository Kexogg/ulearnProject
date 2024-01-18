from django.shortcuts import render


def geography(request):
    return render(request, 'geography.html', {})