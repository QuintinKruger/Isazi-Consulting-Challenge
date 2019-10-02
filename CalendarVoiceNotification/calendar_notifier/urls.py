from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/get_calendar', views.get_calendar, name='get_calendar'),
]
