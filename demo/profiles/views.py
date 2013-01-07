from django.shortcuts import render


def promo(request):
    return render(request, 'static/promo.html')
