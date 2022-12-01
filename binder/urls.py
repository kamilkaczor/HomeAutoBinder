from django.urls import path
from binder import views


urlpatterns = [
    path('', views.index, name='index'),
    path('home_temp/', views.home_temp, name='home_temp'),
    path('reku_temp/', views.reku_temp, name='reku_temp'),
    path('windows_shutters/', views.windows_shutters, name='windows_shutters'),
    path('solar_inverter/', views.solar_inverter, name='solar_inverter'),
    path('create_chart/', views.create_chart, name='create_chart'),
    path('about/', views.about, name='about'),
]
