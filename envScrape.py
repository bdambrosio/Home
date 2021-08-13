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


intvl_total = {}
intvl_count = {}
last_db_update_time = {}

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
    global intvl_total, intvl_count, last_db_update_time, db

    try:
        print (msg.topic, msg.payload)
        topic = msg.topic
        #print(topic, measurement)
        now = utc.localize(datetime.utcnow())
        Time = str(now.astimezone(ptz))[:-13]
        tags = topic.split('/')

        if 'home' in topic: #need to convert rfm brokered msgs to 'tele' format below!
            data = json.loads(msg.payload)
            measure = data['measure']
            if not topic in intvl_total.keys():
                intvl_total[topic] = 0.0 # start new accumulator
                intvl_count[topic] = 0
                last_db_update_time[topic] = time.time() - 601 # because this measurement not in last update
                print (topic, intvl_total.keys())
            intvl_total[topic] += data['value']
            intvl_count[topic] += 1
            int_time = int(time.time())
            if int_time - last_db_update_time[topic] > 600: # more than 1 hr
                try:
                    json_measurement['measurement'] = measure
                    intvl_value = intvl_total[topic]/intvl_count[topic]
                    json_measurement['fields']['value'] = intvl_value
                    json_measurement['fields']['units'] = 'C'
                    json_measurement['tags']['sys'] = tags[0]
                    json_measurement['tags']['subsys'] = tags[1]
                    db.write_points(json_measurements)
                except BaseError as e:
                    print("errror in db write", e)

        elif 'tele' in topic and tags[1] == 'sds011' and tags[2] == 'SENSOR': # std tasmota mqtt format
            data = json.loads(msg.payload)
            topic25 = topic+'2.5 '
            topic10 = topic+'10'
            if not topic in intvl_total.keys():
                # tasmota reports both values of sds011 in a single msg
                intvl_total[topic25] = 0.0 # start new accumulator
                intvl_total[topic10] = 0.0 # start new accumulator
                intvl_count[topic] = 0
                last_db_update_time[topic] = time.time() - 601 # because this measurement not in last update
            intvl_total[topic25] += data['SDS0X1']['PM2.5']
            intvl_total[topic10] += data['SDS0X1']['PM10']
            intvl_count[topic] += 1
            int_time = int(time.time())

            if int_time - last_db_update_time[topic] > 600: # more than 1 hr
                json_measurement['measurement'] = 'particulates'
                json_measurement['fields']['units'] = 'PPM'
                json_measurement['tags']['sys'] = 'env'
                json_measurement['tags']['subsys'] = 'SDS011'
                json_measurement['fields']['value'] = intvl_total[topic25]/intvl_count[topic]
                json_measurement['tags']['subsys2'] = 'PM2.5'
                db.write_points(json_measurements)
                json_measurement['fields']['value'] = intvl_total[topic10]/intvl_count[topic]
                json_measurement['tags']['subsys2'] = 'PM10'
                db.write_points(json_measurements)
                intvl_total[topic10] = 0.0
                intvl_count[topic10] = 0
                intvl_total[topic10] = 0.0
                intvl_count[topic10] = 0
        
    except OSError as e:
        print ("exception caught", e)
        
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
client.subscribe('tele/#')

while True:
    time.sleep(.1)
    client.loop()
