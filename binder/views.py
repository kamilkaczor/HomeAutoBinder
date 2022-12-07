from django.shortcuts import render, redirect
from .models import TemperaturesHome, TemperaturesReku, SolarInverterValues
from .ventilation_cent_mqtt import get_reku_temps
from . solar_inverter import realtime_readings
import subprocess
import re
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    reku_temperature = {}
    #get last values from database
    reku_temperatures_last = TemperaturesReku.objects.latest('id')
    reku_temperatures_ = list(TemperaturesReku.objects.filter(id=reku_temperatures_last.id)\
        .values_list('temp_inlet', 'temp_outlet', 'temp_form_home', 'temp_to_home'))
    reku_temperatures = {
        'Czerpnia': reku_temperatures_[0][0],
        'Wyrzutnia': reku_temperatures_[0][1],
        'Z domu': reku_temperatures_[0][2],
        'Do domu': reku_temperatures_[0][3],
    }
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
    if request.method == 'POST':
        checkboxes = request.POST.getlist('inv_val')
        request.session['checkboxes_inv'] = checkboxes
    return render(request, 'solar_inverter.html', context)


def save_values_to_db():
    reku_temperatures = get_reku_temps()
    home_temperatures = list(get_home_temp().values())
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


def create_chart_home(request):
    plot_data = []
    context = {}
    try:
        checkboxes_home_temp = request.session['checkboxes_home_list']
        sensor_number = ["temp_" + item for item in checkboxes_home_temp]
        fig = make_subplots(rows=1, cols=len(sensor_number))
        for item in range(0, len(sensor_number)):
            time, value = get_values_from_db(TemperaturesHome, QUERRY_DATE, sensor_number[item])
            plot_data = fig.add_trace(go.Scatter(x=time, y=value, mode='lines',
                                                 name=f"Temperatura pokój {checkboxes_home_temp[item]}"),
                                      row=1, col=item+1)
        context = {'plot_div': plot_data.to_html()}
    except Exception as e:
        print(e)
    return render(request, 'chart.html', context)


def create_chart_reku(request):
    plot_data = []
    context = {}
    try:
        checkboxes_reku_temp = request.session['checkboxes_reku_list']
        fig = make_subplots(rows=1, cols=len(checkboxes_reku_temp))
        reku_dict = {
            'Wyrzutnia': 'temp_outlet',
            'Czerpnia': 'temp_inlet',
            'Z domu': 'temp_form_home',
            'Do domu': 'temp_form_home',
        }
        for item in range(0, len(checkboxes_reku_temp)):
            time, value = get_values_from_db(TemperaturesReku, QUERRY_DATE, reku_dict[checkboxes_reku_temp[item]])
            plot_data = fig.add_trace(go.Scatter(x=time, y=value, mode='lines', name=f"Temperatura {checkboxes_reku_temp[item]}"), row=1, col=item+1)
        context = {'plot_div': plot_data.to_html()}
    except Exception as e:
        print(e)
    return render(request, 'chart.html', context)


def create_chart_inv(request):
    plot_data = []
    context = {}
    inv_dict={
        'Voltage L1': 'voltage_L1',
        'Voltage L2': 'voltage_L2',
        'Voltage L3': 'voltage_L3',
        'Current L1': 'current_L1',
        'Current L2': 'current_L2',
        'Current L3': 'current_L3',
        'Energy Today': 'energy_today',
        'Frequency': 'frequency',
        'Average Current AC': 'I_AC',
        'Current DC': 'current_dc',
        'Power AC': 'P_AC',
        'Total Energy': 'energy_total',
        'Average Voltage AC': 'U_AC',
        'Voltage DC': 'voltage_dc',
    }
    try:
        checkboxes_inv_val = request.session['checkboxes_inv']
        fig = make_subplots(rows=int(len(checkboxes_inv_val)), cols=1)

        for item in range(1, len(checkboxes_inv_val)+1):
            time, value = get_values_from_db(SolarInverterValues, QUERRY_DATE, inv_dict[checkboxes_inv_val[item-1]])
            plot_data = fig.add_trace(
                go.Scatter(x=time, y=value, mode='lines', name=f"Inverter {checkboxes_inv_val[item-1]}"), row=item,
                col=1)
        context = {'plot_div': plot_data.to_html()}
    except Exception as e:
        print(e)
    return render(request, 'chart.html', context)


def about(request):
    save_values_to_db()
    return render(request, 'about.html')


def get_values_from_db(db_name, date, fil_arg):
    time = list(db_name.objects.filter(date__month=date).values_list('time', flat=True))
    time = [item.strftime("%H:%M:%S") for item in time]
    querry_from_db = list(db_name.objects.filter(date__month=date).values_list(fil_arg, flat=True))
    querry_from_db = [float(item) for item in querry_from_db]
    return time, querry_from_db

