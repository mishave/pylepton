import os
import subprocess
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("triggerthermal")
    client.subscribe("triggerhires")
    client.subscribe("triggerboth")

def on_message(client, userdata, msg):
    if msg.topic == "triggerthermal":
        data = json.loads(msg.payload)
        captureimage(data, 1)
    if msg.topic == "triggerhires":
        data = json.loads(msg.payload)
        captureimage(data, 2)
    if msg.topic == "triggerboth":
        data = json.loads(msg.payload)
        captureimage(data, 3)

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

def captureimage(data, trigger):
    timestamp = data.get('timestamp')

    # Print the timestamp
    print(f"Received timestamp: {timestamp}")
    # Process the request data and generate a response
    # You can implement your custom logic here
    # For example, you can access the request data using data['key']
    # and generate a response based on that

    # Run the thermalImage.py script
    script_path = "/home/pi/CRKDcabinet/pylepton/thermalImage.py"
    dir_path = "/home/pi/CRKDcabinet/homeassistant/config/www/thermal/"
    device = "/dev/spidev0.0"
    stamp = timestamp
    command = f"python3 {script_path} {dir_path} {device} {stamp}"
    print(command)
    print(trigger)

    if trigger == 1 or trigger == 3:
        print("triggering thermal")
        try:
            image = subprocess.run(command, shell=True, check=True)
            response = {
                'status': 'finished',
                'result': 'success',
                'message': 'Script executed successfully'
            }
        except subprocess.CalledProcessError as e:
            response = {
                'status': 'finished',
                'result': 'fail',
                'message': f'Script execution failed: {e}'
            }

        client.publish("thermal_status", json.dumps(response))
        print (response)
    if trigger == 2 or trigger == 3:
        print("triggering hires")
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