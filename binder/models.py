from django.db import models
from datetime import datetime

class TemperaturesReku(models.Model):
    date = models.DateField()
    time = models.TimeField()
    temp_inlet = models.FloatField()
    temp_outlet = models.FloatField()
    temp_form_home = models.FloatField()
    temp_to_home = models.FloatField()


class TemperaturesHome(models.Model):
    date = models.DateField()
    time = models.TimeField()
    temp_1 = models.FloatField()
    temp_2 = models.FloatField()
    temp_3 = models.FloatField()
    temp_4 = models.FloatField()


class SolarInverterValues(models.Model):
    date = models.DateField()
    time = models.TimeField()
    voltage_L1 = models.FloatField()
    voltage_L2 = models.FloatField()
    voltage_L3 = models.FloatField()
    current_L1 = models.FloatField()
    current_L2 = models.FloatField()
    current_L3 = models.FloatField()
    energy_today = models.FloatField()
    frequency = models.FloatField()
    I_AC = models.FloatField()
    current_dc = models.FloatField()
    P_AC = models.FloatField()
    energy_total = models.FloatField()
    U_AC = models.FloatField()
    voltage_dc = models.FloatField()

