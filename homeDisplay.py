# Home plug control  display for Pi0 using python3 and PySimpleGUI
import time
from time import ctime
from datetime import datetime
import pytz
import json
import paho.mqtt.client as mqtt
import threading
import PySimpleGUI as sg

def press(btn):
    # need to decode which btn!
    topic = 'cmnd/SP10'+str(btn)+'/POWER'
    try:
        rc = client.publish(topic, 'TOGGLE')
        window['-status-'].update(topic+' TOGGLE')
    except:
        window['-status-'] = "publish error"

    
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Button('1', key='-1-'), sg.Text('OFF', key='-status1-'),
             sg.Button('2', key='-2-'), sg.Text('OFF', key='-status2-') ],
            [sg.Button('3', key='-3-'), sg.Text('OFF', key='-status3-'),
             sg.Button('4', key='-4-'), sg.Text('OFF', key='-status4-')],
            [sg.Text('stat/XXXXX/XXXXX XXXXX', key='-status-')]
]
            
            # Create the Window
window = sg.Window('Plugs', layout, no_titlebar=True)

#setup to receive
def new_msg(client, userdata, msg):
    #print ("new msg", msg.topic, msg.payload)
    window['-status-'].update(str(msg.topic)+' '+msg.payload.decode('utf-8'))
    if 'stat' in msg.topic and 'POWER' in msg.topic:
        btn = msg.topic[9]
        if b'ON' in msg.payload:
            window['-status'+btn+'-'].update(' ON')
        elif b'OFF' in msg.payload:
            window['-status'+btn+'-'].update('OFF')
            

mqtt_rc = -1   
def on_connect(client, userdata, flags, rc):
    global mqtt_rc
    mqtt_rc = rc

def on_publish(client,userdata,result):             #create function for callback
    #print("data published ", result)
    pass

client = mqtt.Client() 
client.on_connect = on_connect
client.on_message = new_msg
client.on_publish = on_publish
client.username_pw_set(username='mosq', password='1947nw')
client.connect("192.168.1.117", 1883, 60) 

# for control of ac battery charger when battery voltage gets too low, tbd
#client.subscribe('pv.battery.input.voltage')
#client.subscribe("pv.battery.input.current")

#client.subscribe('stat/SP101/RESULT')
client.subscribe('stat/SP101/POWER')
client.subscribe('stat/SP102/POWER')
client.subscribe('stat/SP103/POWER')
client.subscribe('stat/SP104/POWER')

def PSGEvents():
    window.finalize()
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
t2 = threading.Thread(target=MQTT_Msgs)
t1.start()
#t2.start()
client.loop_forever()








