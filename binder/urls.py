from django.urls import path
from binder import views


urlpatterns = [
    path('', views.index, name='index'),
    path('home_temp/', views.home_temp, name='home_temp'),
    path('reku_temp/', views.reku_temp, name='reku_temp'),
    path('windows_shutters/', views.windows_shutters, name='windows_shutters'),
    path('solar_inverter/', views.solar_inverter, name='solar_inverter'),
    path('create_chart_home/', views.create_chart_home, name='create_chart_home'),
    path('create_chart_reku/', views.create_chart_reku, name='create_chart_reku'),
    path('create_chart_inv/', views.create_chart_inv, name='create_chart_inv'),
    path('about/', views.about, name='about'),
]
