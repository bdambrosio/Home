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
S2_vols = ' 000.0'

S3_temp = ' 00.0'
S3_hum = ' 00.0'
S3_atmp = ' 0000.0'

S4_temp = ' 00.0'
S4_hum = ' 00.0'

PM25 = ' 000.0'
PM10 = ' 000.0'
Msg = '                '
ptz = pytz.timezone('America/Los_Angeles')
utc = pytz.timezone('UTC')
now = utc.localize(datetime.utcnow())
Time = str(now.astimezone(ptz))[:-13]

import PySimpleGUI as sg
sg.theme('DarkAmber')   # Add a little color to your windows
sg.set_options(font=('Helvetica', 24))
# 
layout = [  [sg.Text('    '), sg.Text(Time, key='-time-')],

            [sg.Text('     T:'), sg.Text(S4_temp, key='-S4_temp-'),
             sg.Text('     H:'), sg.Text(S4_hum, key='-S4_hum-')],

            [sg.Text('     PM2.5:'), sg.Text(PM25, key='-PM25-'),
             sg.Text(' PM10:'), sg.Text(PM10, key='-PM10-')],

            [sg.Text('      '), sg.Button('PvChrg', key='-SP101-'),
             sg.Text('      '), sg.Button(' Porch ', key='-SP102-'), sg.Text('    ')],
            [sg.Text('      '), sg.Button('    Htr   ', key='-SP103-'),
             sg.Text('      '), sg.Button('Bdm Htr', key='-SP104-')]
]

# Create the Window
window = sg.Window('Home', layout, no_titlebar=True)

def new_measurement(client, userdata, msg):
    #print (msg.topic, msg.payload)
    now = utc.localize(datetime.utcnow())
    Time = str(now.astimezone(ptz))[:-13]
    topic = msg.topic

    """
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
    """
    if 'home' in topic:
        tags = topic.split('/')
        measure = tags[2]
        try:
            measurement = json.loads(msg.payload)
        except:
            return
        value = measurement['value']
        """
        if tags[1] == 'sensor2':
            if measure == 'tmp':
                S2_temp = " {0:5.2f}".format(value*9/5+32)
                window['-S2_temp-'].update(S2_temp)
            elif measure == 'hum':
                S2_hum = " {0:5.2f}".format(value)
                window['-S2_hum-'].update(S2_hum)
            elif measure == 'atmp':
                S2_atmp = " {0:5.1f}".format(value)
                window['-S2_atmp-'].update(S2_atmp)
            elif measure == 'vols':
                S2_vols = " {0:5.1f}".format(value/1000.0)
                window['-S2_vols-'].update(S2_vols)
            
        if tags[1] == 'sensor3':
            if measure == 'tmp':
                S3_temp = " {0:5.2f}".format(value*9/5+32)
                window['-S3_temp-'].update(S3_temp)
            elif measure == 'hum':
                S3_hum = " {0:5.1f}".format(value)
                window['-S3_hum-'].update(S3_hum)
            elif measure == 'atmp':
                S3_atmp = " {0:5.1f}".format(value)
                window['-S3_atmp-'].update(S3_atmp)
            
        """
        if (tags[1] == 'sensor4') or (tags[1] == 'sensor6'):
            if measure == 'tmp':
                S4_temp = " {0:5.2f}".format(value*9/5+32)
                window['-S4_temp-'].update(S4_temp)
            elif measure == 'hum':
                S4_hum = " {0:5.1f}".format(value)
                window['-S4_hum-'].update(S4_hum)


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

    elif 'stat/SP10' in topic:
        start = topic.index("SP10")
        id = topic[start:start+5]
        #print(topic, id, msg.payload)
        if 'POWER' in topic:
            try:
                status = msg.payload
                if status == b'ON':
                    window['-'+id+'-'].update(button_color=('black', 'green'))
                elif status == b'OFF':
                    window['-'+id+'-'].update(button_color=('white', 'grey'))
            except:
                print("failure reading/setting button status")
                return
    else:
                print('unknown: ', topic)
            
def subscribe(client):
    #client.subscribe('pv/battery/output/voltage')
    #client.subscribe("pv/battery/output/current")
    #client.subscribe('pv/battery/input/voltage')
    #client.subscribe("pv/battery/input/current")
    
    client.subscribe('home/#')
    
    client.subscribe('tele/sds011/#')
    
    client.subscribe('stat/SP101/#')
    client.subscribe('stat/SP102/#')
    client.subscribe('stat/SP103/#')
    client.subscribe('stat/SP104/#')
    
# start mqtt client
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        subscribe(client)
        #window['-msg-'].update("MQTT connected")
        print("MQTT connect success")
    else:
        print(f"MQTT connect fail with code {rc}")

def on_disconnect(client, userdata, rc):
    #window['-msg-'].update("MQTT connection lost")
    connected = False
    while connected == False:
        try:
            client.reconnect()
            connected = True
        except:
            pass
    subscribe(client)

def PSGEvents():
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        print(event)
        if '-SP10' in event:
            btn_id=int(event[5])
            print("SW", event)
            if btn_id > 0 and btn_id <= 4:
                print('cmnd/SP10'+str(btn_id)+'/POWER', 'TOGGLE')
                client.publish('cmnd/SP10'+str(btn_id)+'/POWER', 'TOGGLE')
    window.close()

def MQTT_Msgs():
    time.sleep(1)
    client.loop_start()
    time.sleep(1)
    while True:
        try:
            client.publish('cmnd/SP101/Power')
            client.publish('cmnd/SP102/Power')
            client.publish('cmnd/SP103/Power')
            client.publish('cmnd/SP104/Power')
        except BaseException as e:
            print ("exception asking for SP10x Power status", e)
        time.sleep(600) # query every 10 min
            
t1 = threading.Thread(target=PSGEvents)
t1.start()
time.sleep(4) # allow window to be created
        
print("New MQT session being set up")
client = mqtt.Client() 
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = new_measurement
client.username_pw_set(username='mosq', password='1947nw')
client.connect("192.168.1.101", 1883, 60)
t2 = threading.Thread(target=MQTT_Msgs)
t2.start()



