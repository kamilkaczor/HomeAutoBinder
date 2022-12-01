from binder.celery import Celery
from binder.models import TemperaturesHome, TemperaturesReku

from datetime import datetime
from .views import get_home_temp
from .ventilation_cent_mqtt import get_reku_temps
from .solar_inverter import realtime_readings


DATE = datetime.today().strftime('%Y-%m-%d')
TIME = datetime.today().strftime('%H:%M:%S')
app = Celery()

@app.task
def save_home_temp_to_db():
    temp_list = []
    for key, value in get_home_temp().items():
        temp_list.append(value)
    home_temp = TemperaturesHome(date=DATE, time=TIME, temp_1=temp_list[0],
                                 temp_2=temp_list[1], temp_3=temp_list[2],
                                 temp_4=temp_list[3])
    home_temp.save()


@app.task
def save_reku_to_db():
    reku_list = []
    for key, value in get_reku_temps().items():
        reku_list.append(value)
    reku_temps = TemperaturesReku(date=DATE, time=TIME, temp_inlet=reku_list[0], temp_form_home=reku_list[1],
                                  temp_to_home=reku_list[2], temp_outlet=reku_list[3])
    reku_temps.save()


@app.task
def save_inverter_to_db():
    inv_val = realtime_readings().item
    inverter_values = TemperaturesReku(date=DATE, time=TIME,
                                       voltage_L1=inv_val['voltage_L1'],
                                       voltage_L2=inv_val['voltage_L2'],
                                       voltage_L3=inv_val['voltage_L3'],
                                       current_L1=inv_val['current_L1'],
                                       current_L2=inv_val['current_L2'],
                                       current_L3=inv_val['current_L3'],
                                       energy_today=inv_val['energy_today'],
                                       frequency=inv_val['frequency'],
                                       I_AC=inv_val['I_AC'],
                                       current_dc=inv_val['current_dc'],
                                       P_AC=inv_val['P_AC'],
                                       energy_total=inv_val['energy_total'],
                                       U_AC=inv_val['U_AC'],
                                       voltage_dc=inv_val['voltage_dc'])
    inverter_values.save()
