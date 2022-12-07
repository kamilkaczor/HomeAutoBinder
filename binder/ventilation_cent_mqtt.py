import paho.mqtt.client as mqtt
import random, os, time
from datetime import datetime


#mqtt settings
broker = 'openhab'
port = 1883
czerpnia = "/rekuperator/1/1"
do_domu = "/rekuperator/1/2"
z_domu = "/rekuperator/1/3"
wyrzutnia = "/rekuperator/2/1"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = os.environ['MQTT_USERNAME']
password = os.environ['MQTT_PASS']
reku_temps = {}
DATE = datetime.today().strftime('%Y-%m-%d')
TIME = datetime.today().strftime('%H:%M:%S')


def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    if message.topic == "/rekuperator/1/1":
        reku_temps['Czerpnia'] = message.payload.decode("utf-8")
    elif message.topic == "/rekuperator/1/2":
        reku_temps['Z domu'] = message.payload.decode("utf-8")
    elif message.topic == "/rekuperator/1/3":
        reku_temps['Do domu'] = message.payload.decode("utf-8")
    elif message.topic == "/rekuperator/2/1":
        reku_temps['Wyrzutnia'] = message.payload.decode("utf-8")

def on_connect(client, userdata, flags, rc):
   if rc == 0:
      print("connected ok")
   else:
       print(f"connection error {rc}")

def get_reku_temps():
    client = mqtt.Client(client_id) #create new instance
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    print("connecting to broker")
    client.on_message = on_message
    client.connect(broker)
    client.loop_start()
    client.subscribe(czerpnia)
    client.subscribe(z_domu)
    client.subscribe(do_domu)
    client.subscribe(wyrzutnia)
    time.sleep(30) # wait
    #print(reku_temps)
    client.loop_stop()
    return reku_temps