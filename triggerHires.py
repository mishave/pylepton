import os
import subprocess
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hirestrigger")

def on_message(client, userdata, msg):
    if msg.topic == "hirestrigger":
        hirestrigger()

def hirestrigger():
    # Run the libcamera-still command
    command = "libcamera-still -t 5000 -n -o /home/pi/CRKDcabinet/homeassistant/config/www/hires/hires_latest.png"
    try:
        subprocess.run(command, shell=True, check=True)
        response = {
            'status': 'finished',
            'result': 'success',
            'message': 'Capture command executed successfully'
        }
    except subprocess.CalledProcessError as e:
        response = {
            'status': 'finished',
            'result': 'fail',
            'message': f'Capture command execution failed: {e}'
        }

    client.publish("hires_status", json.dumps(response))

if __name__ == '__main__':
    server_ip = os.environ.get("localhost", '0.0.0.0')
    
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
