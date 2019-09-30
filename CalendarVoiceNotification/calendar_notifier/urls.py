from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/quickstart', views.quickstart, name='quickstart'),
]