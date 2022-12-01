from datetime import datetime
import os, requests
import collections

INVERTER_ADDRESS = os.environ['SOLAR_INV']
inverter_values = collections.OrderedDict()
querry_realtime_AC = "http://" + INVERTER_ADDRESS + \
                     "/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=3PInverterData"
querry_realtime_power = "http://" + INVERTER_ADDRESS + \
                        "/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=01&DataCollection=" \
                        "CommonInverterData"

def get_data(querry):
    try:
        r = requests.get(querry, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        print("Przekroczono czas oczekiwania na {}".format(querry))
    except requests.exceptions.RequestException as e:
        print("Wyjątek  {}".format(e))
    return exit()

def realtime_readings():

    inverter_values['Voltage L1'] = get_data(querry_realtime_AC)['Body']['Data']['UAC_L1']['Value']
    inverter_values['Voltage L2'] = get_data(querry_realtime_AC)['Body']['Data']['UAC_L2']['Value']
    inverter_values['Voltage L3'] = get_data(querry_realtime_AC)['Body']['Data']['UAC_L3']['Value']
    inverter_values['Current L1'] = get_data(querry_realtime_AC)['Body']['Data']['IAC_L1']['Value']
    inverter_values['Current L2'] = get_data(querry_realtime_AC)['Body']['Data']['IAC_L2']['Value']
    inverter_values['Current L3'] = get_data(querry_realtime_AC)['Body']['Data']['IAC_L3']['Value']
    inverter_values['Energy Today'] = round(
        get_data(querry_realtime_power)['Body']['Data']['DAY_ENERGY']['Value'] / 1000, 2)
    inverter_values['Frequency'] = get_data(querry_realtime_power)['Body']['Data']['FAC']['Value']
    inverter_values['Average Current AC'] = get_data(querry_realtime_power)['Body']['Data']['IAC']['Value']
    inverter_values['Current DC'] = get_data(querry_realtime_power)['Body']['Data']['IDC']['Value']
    inverter_values['Power AC'] = get_data(querry_realtime_power)['Body']['Data']['PAC']['Value']
    inverter_values['Total Energy'] = round(
        get_data(querry_realtime_power)['Body']['Data']['TOTAL_ENERGY']['Value'] / 1000, 2)
    inverter_values['Average Voltage AC'] = get_data(querry_realtime_power)['Body']['Data']['UAC']['Value']
    inverter_values['Voltage DC'] = get_data(querry_realtime_power)['Body']['Data']['UDC']['Value']
    return inverter_values

