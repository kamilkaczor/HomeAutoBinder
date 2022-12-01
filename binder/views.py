from django.shortcuts import render, redirect
from .models import TemperaturesHome, TemperaturesReku, SolarInverterValues
from .ventilation_cent_mqtt import get_reku_temps
from . solar_inverter import realtime_readings
import subprocess
import re
from datetime import datetime, timedelta
from plotly.offline import plot
import plotly.graph_objects as go
from django.utils import timezone
from plotly.graph_objs import Scatter, Layout
DATE = datetime.now().strftime('%Y-%m-%d')
TIME = datetime.now().strftime('%H:%M:%S')
QUERRY_DATE = datetime.now().strftime("%m")

def index(request):
    return render(request, 'base.html')


def get_home_temp():
    temperatures = {}
    get_sensors = subprocess.run(['ls', '/sys/bus/w1/devices/'], capture_output=True)
    temperature_sensors = get_sensors.stdout.decode("utf-8").split("\n")
    for sensor in temperature_sensors[0:-2]:
        sensor_address = '/sys/bus/w1/devices/' + sensor + '/w1_slave'
        get_temp = subprocess.run(['cat', sensor_address], capture_output=True).stdout.decode("utf-8")
        temp = float(re.findall('\d\d\d\d\d', get_temp)[0])/1000
        temperatures[sensor] = temp
    print(temperatures.values())
    return temperatures

def home_temp(request):
    context = {}
    temperatures = get_home_temp()
    context['temperatures'] = temperatures
    checkboxes = request.POST.getlist('home_temp')
    request.session['checkboxes_home_list'] = checkboxes
    return render(request, 'home_temp.html', context)


def reku_temp(request):
    context = {}
    reku_temperatures = get_reku_temps()
    context['reku_temperatures'] = reku_temperatures
    if request.method == 'POST':
        checkboxes = request.POST.getlist('reku_temp')
        request.session['checkboxes_reku_list'] = checkboxes
    return render(request, 'reku_temp.html', context)


def windows_shutters(request):
    return render(request, 'windows_shutters.html', )


def solar_inverter(request):
    context = {}
    inverter_values = realtime_readings()
    context['inverter_values'] = inverter_values
    return render(request, 'solar_inverter.html', context)

def save_values_to_db():
    reku_temperatures = get_reku_temps()
    home_temperatures = list(get_home_temp().values()) #dict to list of values
    inverter_values = realtime_readings()
    t1 = TemperaturesReku(date=DATE, time=TIME, temp_inlet=reku_temperatures['Czerpnia'],
                          temp_outlet=reku_temperatures['Wyrzutnia'], temp_form_home=reku_temperatures['Z domu'],
                          temp_to_home=reku_temperatures['Do domu'])
    t1.save()
    t2 = TemperaturesHome(date=DATE, time=TIME, temp_1=home_temperatures[0], temp_2=home_temperatures[1],
                          temp_3=home_temperatures[2], temp_4=home_temperatures[3],)
    t2.save()
    inverter = SolarInverterValues(date=DATE, time=TIME, voltage_L1=inverter_values['Voltage L1'],
                                   voltage_L2=inverter_values['Voltage L2'], voltage_L3=inverter_values['Voltage L3'],
                                   current_L1=inverter_values['Current L1'], current_L2=inverter_values['Current L2'],
                                   current_L3=inverter_values['Current L3'], energy_today=inverter_values['Energy Today'],
                                   frequency=inverter_values['Frequency'], I_AC=inverter_values['Average Current AC'],
                                   current_dc=inverter_values['Current DC'], P_AC=inverter_values['Power AC'],
                                   energy_total=inverter_values['Total Energy'], U_AC=inverter_values['Average Voltage AC'],
                                   voltage_dc=inverter_values['Voltage DC'],)
    inverter.save()


def create_chart(request):
    time = []
    querry_from_db = []

    context = {}
    #try:
    checkboxes_home_temp = request.session['checkboxes_home_list']
    sensor_number = ["temp_" + item for item in checkboxes_home_temp]
    print(sensor_number)
    for item in range(0, len(sensor_number)):
        time, value = get_values_from_db(TemperaturesHome, QUERRY_DATE, sensor_number[item])
        print(time, value)
        plot_data = add_series(time, value)

    context = {'plot_div': plot_data}

    return render(request, 'chart.html', context)

def about(request):
    save_values_to_db()
    return render(request, 'about.html')

def get_values_from_db(db_name, date, fil_arg):
    time = list(db_name.objects.filter(pub_date__month=date).values_list('time', flat=True))
    time = [item.strftime("%H:%M:%S") for item in time]
    querry_from_db = list(db_name.objects.filter(pub_date__month=date).values_list(fil_arg, flat=True))
    querry_from_db = [float(item) for item in querry_from_db]
    return time, querry_from_db


def add_series(x, y):
    graphs = []
    graphs.append(go.Scatter(x=x, y=y, mode='lines', name='chart'))
    layout = {
        'title': ' ',
        'xaxis_title': 'Time',
        'yaxis_title': 'Value',
        'height': 1200,
        'width': 1200,
    }
    plot_div = plot({'data': graphs, 'layout': layout}, output_type='div')
    return plot_div