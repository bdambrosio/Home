# pv display for Pi0 using python3 and PySimpleGUI
import time
from time import ctime
from datetime import datetime
import pytz
import json
import paho.mqtt.client as mqtt
import threading

PVB_Vin = ' 00.0'
PVB_Vout = ' 00.0'
PVB_Iin = ' 00.00'
PVB_Iout = ' 00.00'

S2_temp = ' 00.0'
S2_hum = ' 00.0'
S2_atmp = ' 0000.0'

S3_temp = ' 00.0'
S3_hum = ' 00.0'
S3_atmp = ' 0000.0'

PM25 = ' 000.0'
PM10 = ' 000.0'
Msg = '                '
ptz = pytz.timezone('America/Los_Angeles')
utc = pytz.timezone('UTC')
now = utc.localize(datetime.utcnow())
Time = str(now.astimezone(ptz))[:-13]

import PySimpleGUI as sg
sg.theme('DarkAmber')   # Add a little color to your windows
sg.set_options(font=('Helvetica', 14))
# 
layout = [  [sg.Text(Time, key='-time-')],
            [sg.Text('PvB Vi/o:'), sg.Text(PVB_Vin, key='-PVB_Vin-'),
            sg.Text('/'), sg.Text(PVB_Vout, key='-PVB_Vout-'),
             sg.Text(' Ii/o:'), sg.Text(PVB_Iin, key='-PVB_Iin-'),
             sg.Text('/'), sg.Text(PVB_Iout, key='-PVB_Iout-')],

            [sg.Text('S2 T:'), sg.Text(S2_temp, key='-S2_temp-'),
            sg.Text('H:'), sg.Text(S2_hum, key='-S2_hum-'),
             sg.Text('P:'), sg.Text(S2_atmp, key='-S2_atmp-'),
             sg.Text('PM2.5:'), sg.Text(PM25, key='-PM25-')],

            [sg.Text('S3 T:'), sg.Text(S3_temp, key='-S3_temp-'),
            sg.Text('H:'), sg.Text(S3_hum, key='-S3_hum-'),
             sg.Text('P:'), sg.Text(S3_atmp, key='-S3_atmp-'),
             sg.Text('PM10:'), sg.Text(PM10, key='-PM10-')],

            [sg.Button('0', key='SW0'),sg.Button('1', key='SW1'),
             sg.Button('2', key='SW2'),sg.Button('3', key='SW3')],
            [sg.Text(Msg, key='-msg-')]
]

# Create the Window
window = sg.Window('PV Monitor', layout, no_titlebar=True)

def new_measurement(client, userdata, msg):
    #print (msg.topic, msg.payload)
    now = utc.localize(datetime.utcnow())
    Time = str(now.astimezone(ptz))[:-13]
    topic = msg.topic

    if 'pv/battery' in topic:
        try:
            measurement = json.loads(msg.payload)
        except:
            return
        #print(topic, measurement)
        window['-time-'].update(Time)
        if 'output' in topic:
            if 'current' in topic:
                PVB_Iout = " {0:5.2f}".format(measurement)
                window['-PVB_Iout-'].update(PVB_Iout)
            else:
                PVB_Vout = " {0:5.2f}".format(measurement)
                window['-PVB_Vout-'].update(PVB_Vout)
        
        elif 'input' in topic:
            if 'current' in topic:
                PVB_Iin = " {0:5.2f}".format(measurement)
                window['-PVB_Iin-'].update(PVB_Iin)
            else:
                PVB_Vin = " {0:5.2f}".format(measurement)
                window['-PVB_Vin-'].update(PVB_Vin)
    elif 'home' in topic:
        tags = topic.split('/')
        measure = tags[2]
        try:
            measurement = json.loads(msg.payload)
        except:
            return
        value = measurement['value']
        if tags[1] == 'sensor2':
            if measure == 'tmp':
                S2_temp = " {0:5.2f}".format(value*9/5+32)
                window['-S2_temp-'].update(S2_temp)
            elif measure == 'hum':
                S2_hum = " {0:5.2f}".format(value)
                window['-S2_hum-'].update(S2_hum)
            elif measure == 'atmp':
                S2_atmp = " {0:5.2f}".format(value)
                window['-S2_atmp-'].update(S2_atmp)
            
        if tags[1] == 'sensor3':
            if measure == 'tmp':
                S3_temp = " {0:5.2f}".format(value*9/5+32)
                window['-S3_temp-'].update(S3_temp)
            elif measure == 'hum':
                S3_hum = " {0:5.2f}".format(value)
                window['-S3_hum-'].update(S3_hum)
            elif measure == 'atmp':
                S3_atmp = " {0:5.2f}".format(value)
                window['-S3_atmp-'].update(S3_atmp)
            
    elif topic == 'tele/sds011/SENSOR':
        try:
            measurement = json.loads(msg.payload)
        except:
            return
        pm25_val = measurement['SDS0X1']['PM2.5']
        pm10_val = measurement['SDS0X1']['PM10']
        PM25= " {0:6.1f}".format(pm25_val)
        window['-PM25-'].update(PM25)
        PM10 = " {0:6.1f}".format(pm10_val)
        window['-PM10-'].update(PM10)

    elif 'SP10' in topic:
        id = int(topic[9])
        print(topic, id)
        if 'RESULT' in topic:
            try:
                change = json.loads(msg.payload)
            except:
                return
            if change is dict:
                print(change.keys())
    else:
                print('unknown: ', topic)
            
    
# start mqtt client
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe('pv/battery/output/voltage')
        client.subscribe("pv/battery/output/current")
        client.subscribe('pv/battery/input/voltage')
        client.subscribe("pv/battery/input/current")
        
        client.subscribe('home/#')

        client.subscribe('tele/sds011/#')

        client.subscribe('stat/SP101/#')
        client.subscribe('stat/SP102/#')
        client.subscribe('stat/SP103/#')
        client.subscribe('stat/SP104/#')
        print("MQTT connect success")
    else:
        print(f"MQTT connect fail with code {rc}")

def on_disconnect(client, userdata, rc):
    client.reconnect()

        
print("New MQT session being set up")
client = mqtt.Client() 
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = new_measurement
client.username_pw_set(username='mosq', password='1947nw')
client.connect("192.168.1.117", 1883, 60) 

#client.subscribe('pv/battery/output/voltage')
#client.subscribe("pv/battery/output/current")
#client.subscribe('pv/battery/input/voltage')
#client.subscribe("pv/battery/input/current")

#client.subscribe('stat/SP101/#')
#client.subscribe('stat/SP102/#')
#client.subscribe('stat/SP103/#')
#client.subscribe('stat/SP104/#')

def PSGEvents():
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if 'SW' in event:
            btn_id=int(event[2])
            print(event)
            if btn_id >= 0 and btn_id < 4:
                client.publish('cmnd/SP10'+str(btn_id)+'/POWER', 'OFF')
            
            
    window.close()

def MQTT_Msgs():
    while True:
        client.loop()
        time.sleep(1)
        
t1 = threading.Thread(target=PSGEvents)
t2 = threading.Thread(target=MQTT_Msgs)
t1.start()
t2.start()



