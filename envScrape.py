import time as utime
import json
import socket
import time
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import sys
from time import ctime
from datetime import datetime
import pytz
import math

ptz = pytz.timezone('America/Los_Angeles')
utc = pytz.timezone('UTC')
now = utc.localize(datetime.utcnow())
Time = str(now.astimezone(ptz))[:-13]

db = InfluxDBClient(host='localhost', port=8086)
db.switch_database('env')

json_measurement =  {
    "measurement": "temperature",
    "tags": {
        "sys": "env",
        "subsys": "s1",
        #loc": "indoors",
        #loc2": "kitchen",
        #time": "2018-03-28T8:01:00Z",
    },
    "fields": {
        "value": 127,
        "units": 'C'
    }
}

json_measurements = [json_measurement]
last_humidity = 0

def update_db(topic, value):
    global db
    print (topic, value)

#setup to publish to mosquitto broker
def new_measurement(client, userdata, msg):
    global last_humidity
    topic = msg.topic
    data = json.loads(msg.payload)
    #print(topic, measurement)
    now = utc.localize(datetime.utcnow())
    Time = str(now.astimezone(ptz))[:-13]
    print (topic, data)
    tags = topic.split('/')
    measure = data['measure']
    json_measurement['measurement'] = measure
    json_measurement['fields']['value'] = data['value']
    json_measurement['fields']['units'] = 'C'
    json_measurement['tags']['sys'] = tags[0]
    json_measurement['tags']['subsys'] = tags[1]
    print (json_measurement)
    db.write_points(json_measurements)

    if measure == 'hum':
        last_humidity = data['value']
    if measure == 'vols' and data['value'] > 0:
        iaq = math.log(data['value']) + 0.04 * last_humidity
        json_measurement['measurement'] = 'iaq'
        json_measurement['fields']['value'] = iaq
        json_measurement['fields']['units'] = 'iaq'
        json_measurement['tags']['sys'] = tags[0]
        json_measurement['tags']['subsys'] = tags[1]
        print (json_measurement)
        db.write_points(json_measurements)
        
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connect success")
    else:
        print(f"MQTT connect fail with code {rc}")

def on_publish(client,userdata,result):             #create function for callback
    #print("data published ", result)
    pass

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = new_measurement
client.on_publish = on_publish
client.username_pw_set(username='mosq', password='1947nw')
client.connect("127.0.0.1", 1883, 60) 
client.subscribe("home/#")

while True:
    time.sleep(1)
    client.loop()
