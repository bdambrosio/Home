# Home plug control  display for Pi0 using python3 and PySimpleGUI
import time
from time import ctime
from datetime import datetime
import pytz
import json
import paho.mqtt.client as mqtt
import threading
import PySimpleGUI as sg

Vin = ' 00.0'
Vout = ' 00.0'
Iin = ' 00.00'
Iout = ' 00.00'
ptz = pytz.timezone('America/Los_Angeles')
utc = pytz.timezone('UTC')
now = utc.localize(datetime.utcnow())
Time = str(now.astimezone(ptz))[:-13]

window = None

def press(btn):
    # need to decode which btn!
    topic = 'cmnd/SP10'+str(btn)+'/POWER'
    try:
        rc = client.publish(topic, 'TOGGLE')
        window['-status-'].update(topic+' TOGGLE')
    except:
        window['-status-'] = "publish error"

    
sg.theme('DarkAmber')   # Add a touch of color
sg.set_options(font=('Helvetica', 15))
layout = [  [sg.Text(Time, key='-time-', justification='right')],
            [sg.Button('1', key='-1-', font=('Helvetica', 20)), 
             sg.Button('2', key='-2-', font=('Helvetica', 20)), 
             sg.Button('3', key='-3-', font=('Helvetica', 20)), 
             sg.Button('4', key='-4-', font=('Helvetica', 20))],
            [sg.Text('OFF', size=(3,1), key='-status1-'),
             sg.Text('OFF', size=(3,1), key='-status2-'),
             sg.Text('OFF', size=(3,1),key='-status3-'),
             sg.Text('OFF', size=(3,1),key='-status4-')],
            [sg.Text('BIn  V:', size=(7,1)), sg.Text(Vin, key='-Vin-'),
             sg.Text(' I: '), sg.Text(Iin, key='-Iin-')],
            [sg.Text('BOut V:', size=(7,1)), sg.Text(Vout, key='-Vout-'),
             sg.Text(' I: '), sg.Text(Iout, key='-Iout-')],
            [sg.Text('stat/XXXXX/XXXXX XXXXX', key='-status-')]
]
            
#setup to receive
def new_msg(client, userdata, msg):
    #print ("new msg", msg.topic, msg.payload)
    if window is None:
        return
    window['-status-'].update(str(msg.topic)+' '+msg.payload.decode('utf-8'))
    if 'stat' in msg.topic and 'POWER' in msg.topic:
        btn = msg.topic[9]
        if b'ON' in msg.payload:
            window['-status'+btn+'-'].update(' ON')
        elif b'OFF' in msg.payload:
            window['-status'+btn+'-'].update('OFF')
        return
    topic = msg.topic
    measurement = json.loads(msg.payload)
    #print(topic, measurement)
    now = utc.localize(datetime.utcnow())
    Time = str(now.astimezone(ptz))[:-13]
    window['-time-'].update(Time)
    if 'output' in topic:
        if 'current' in topic:
            Iout = " {0:5.2f}".format(measurement)
            window['-Iout-'].update(Iout)
            print(Iout)
        else:
            Vout = " {0:5.2f}".format(measurement)
            window['-Vout-'].update(Vout)
        
    elif 'input' in topic:
        if 'current' in topic:
            Iin = " {0:5.2f}".format(measurement)
            window['-Iin-'].update(Iin)
        else:
            Vin = " {0:5.2f}".format(measurement)
            window['-Vin-'].update(Vin)
    


mqtt_rc = -1   
def on_connect(client, userdata, flags, rc):
    global mqtt_rc
    mqtt_rc = rc
    print ("MQTT connect", rc)
    if rc == 0:
        # for control of ac battery charger when battery voltage gets too low, tbd
        client.subscribe('pv/battery/input/voltage')
        client.subscribe("pv/battery/input/current")
        client.subscribe('pv/battery/output/voltage')
        client.subscribe("pv/battery/output/current")

        client.subscribe('stat/SP101/POWER')
        client.subscribe('stat/SP102/POWER')
        client.subscribe('stat/SP103/POWER')
        client.subscribe('stat/SP104/POWER')


def on_publish(client,userdata,result):             #create function for callback
    #print("data published ", result)
    pass

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = new_msg
client.on_publish = on_publish
client.username_pw_set(username='mosq', password='1947nw')
client.connect("192.168.1.117", 1883, 60) 

def PSGEvents():
    global window
    # Create the Window
    window = sg.Window('Plugs     Battery', layout, finalize=True)

    if mqtt_rc == 0:
        window['-status-'].update('MQTT connected')
    else:
        window['-status-'].update('MQTT error')
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # if user closes window
            break
        if callable(event):
            event()
            break
        if event[0] == '-' and event[2] == '-':
            press(event[1])
        
def MQTT_Msgs():
    while True:
        #client.loop()
        time.sleep(1)
        
t1 = threading.Thread(target=PSGEvents)
t1.start()
#give window a chance to start
time.sleep(2)
client.loop_forever()








