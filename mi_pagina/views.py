from django.shortcuts import render

from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>¡Hola Mundo! Esta es mi primera página con Django.</h1>")

from django.contrib.auth.decorators import login_required

@login_required
def mi_curriculum(request):
    return render(request, 'cv.html')