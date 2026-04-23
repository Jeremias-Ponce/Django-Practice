from django.urls import path
from . import views

# Revisa que no diga "urlpattern" (sin la s) o "URLPatterns" (en mayúsculas)
urlpatterns = [
    path('', views.mi_curriculum, name='curriculum'),
]