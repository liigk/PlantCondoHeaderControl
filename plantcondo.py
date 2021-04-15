
#!/usr/bin/env python
import time
import serial
import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
import json
import trionesControl.trionesControl as tc
import pygatt


counter = 0
complete = False
level_1 = 40
level_0 = 10
error_code = False

ser = serial.Serial(
        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

def on_connect1(client, userdata, flags, rc):
    print("Client 1 Connected with result code "+str(rc))
    client1.subscribe("test/response")    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global complete
    global counter
    global level_1
    global error_code
    instruction = msg.payload.decode('utf-8')
    print(instruction)
    data = json.loads(instruction)
    
    if(data["task_type"] == "AD"): #abiant measure
        ser.write("temphumid".encode())
        time.sleep(5)
        line = ser.read(100).decode()
        return_data = line.split(",")
        client.publish("response", json.dumps({
            'task_id': data["task_id"],
            'succeeded': True,
            'ambient_humidity': return_data[0],
            'ambient_light_intensity': return_data[2],
            'ambient_temperature': return_data[1]
        }))
    elif(data["task_type"] == "LC"):#lighting
        print(data)
        device = tc.connect('58:82:04:00:09:2E')
        tc.powerOn(device)
        tc.setRGB(data["desired_light_red"], data["desired_light_green"], data["desired_light_blue"],device)
        client.publish("response", json.dumps({
			'task_id': data["task_id"],
			'succeeded': True,
        }))
        
    elif(data["task_type"] == "WT"):#watering
        #move motor
        #engage watering
        if(data["level"] == 1):
            instruction1 = str(level_1)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            instruction2 = str(level_1-4)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            instruction3 = str(level_1)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            instruction4 = str(level_1)+ "," + str(data["radius"]-5)+ "," + str(data["degree"])
            print(instruction1)
            print(instruction2)
            print(instruction3)

        while complete == False:

            if(counter == 0):
                client1.publish("test/request",instruction1)
                while(counter != 1):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	
                ser.write("soil".encode())
            elif(counter == 1):
                client1.publish("test/request", instruction2)
                while(counter != 2):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break
                ser.write("a".encode())
                time.sleep(3)	
                line = ser.read(100).decode()
                data_line = line.split("\r\n")
                print(data_line[0])
                
            elif(counter == 2):
                client1.publish("test/request", instruction3)
                while(counter != 3):
                    time.sleep(1)	
                    if (error_code == True):
                        error_code = False
                        break
                ser.write("a".encode())
            elif(counter == 3):
                counter = 0
                complete = True

        complete = False
        humid = int(data_line[0])
        dif_humid = data["target_humidity"] - humid
        duration = dif_humid / 5
        client1.publish("test/request", instruction4)
        while(counter != 1):
                time.sleep(1)	
                if (error_code == True):
                        error_code = False
                        break

        counter = 0

        com_temp = "-1," + str(duration)+",0"
        
        client1.publish("test/request", com_temp)
        while(counter != 1):
                time.sleep(1)	
        counter = 0

        client.publish("response", json.dumps({
			'task_id': data["task_id"],
			'succeeded': True,
        }))
    elif(data["task_type"] == "SD"):#seeding
        #move motor
        #engage seeding
        print("debug data")
        print (data["seed_container_level"])
        if(data["level"] == 1):
            #move to level 1 and move back humidity sensor
            instruction4 = str(level_1)+ "," + str(data["radius"])+ "," + "0"
            #shove seed into soil
            instruction5 = str(level_1)+ "," + str(data["radius"])+ "," + str(data["degree"])
            #raise it up
            instruction6 = str(level_1 - 8)+ "," + str(data["radius"])+ "," + str(data["degree"])
            instruction7 = str(level_1)+ "," + str(data["radius"])+ "," + str(data["degree"])
            print("here level 1")

        if(data["seed_container_level"] == 0):
            # to level 0
            instruction0 = str(level_0)+ "," + str(data["seed_container_radius"])+ "," + "0"
            # to seed position
            instruction1 = str(level_0)+ "," + str(data["seed_container_radius"])+ "," + str(data["seed_container_degree"])
            # down pickup seed
            instruction2 = str(level_0 - 4)+ "," + str(data["seed_container_radius"])+ "," + str(data["seed_container_degree"])
            # up to move back humidity sensor
            instruction3 = str(level_0)+ "," + str(data["seed_container_radius"])+ "," + str(data["seed_container_degree"])
            print("here level 0")
        print(instruction0)

        while complete == False:

            if(counter == 0):
                client1.publish("test/request",instruction0)
                while(counter != 1):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	
                ser.write("grip_open".encode())
            elif(counter == 1):
                client1.publish("test/request", instruction1)
                while(counter != 2):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	
            elif(counter == 2):
                client1.publish("test/request", instruction2)
                while(counter != 3):
                    time.sleep(1)	
                    if (error_code == True):
                        error_code = False
                        break
                time.sleep(1)	
                ser.write("grip_close".encode())
                time.sleep(3)

            elif(counter == 3):
                client1.publish("test/request", instruction3)
                while(counter != 4):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	

            elif(counter == 4):
                client1.publish("test/request", instruction4)
                while(counter != 5):
                    time.sleep(1)	
                    if (error_code == True):
                        error_code = False
                        break

            elif(counter == 5):
                client1.publish("test/request", instruction5)
                while(counter != 6):
                    time.sleep(1)	
                    if (error_code == True):
                        error_code = False
                        break
                ser.write("grip_open".encode())
                time.sleep(5)


            elif(counter == 6):
                time.sleep(1)	
                ser.write("grip_close".encode())
                client1.publish("test/request", instruction6)
                while(counter != 7):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	

            elif(counter == 7):
                client1.publish("test/request", instruction7)
                while(counter != 8):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	
                time.sleep(1)	
                ser.write("grip_close".encode())    
            elif(counter == 8):
                counter = 0
                complete = True

        complete = False

        print("seeding completed")
            
        client.publish("response", json.dumps({
			'task_id': data["task_id"],
			'succeeded': True,
        }))
    elif(data["task_type"] == "PD"):#soil humidity
        #move motor
        #engage humidity
        if(data["level"] == 1):

            instruction1 = str(level_1)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            instruction2 = str(level_1-4)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            instruction3 = str(level_1)+ "," + str(data["radius"]+4)+ "," + str(data["degree"])
            print(instruction1)
            print(instruction2)
            print(instruction3)

        while complete == False:

            if(counter == 0):
                client1.publish("test/request",instruction1)
                while(counter != 1 and error_code == False):
                    time.sleep(1)	
                    if (error_code == True):
                        error_code = False
                        break
                ser.write("soil".encode())

            elif(counter == 1):
                client1.publish("test/request", instruction2)
                while(counter != 2):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break
                ser.write("a".encode())
                time.sleep(3)	
                line = ser.read(100).decode()
                data_line = line.split("\r\n")
                print(data_line[0])

            elif(counter == 2):
                client1.publish("test/request", instruction3)
                while(counter != 3):
                    time.sleep(1)
                    if (error_code == True):
                        error_code = False
                        break	
                ser.write("a".encode())
            elif(counter == 3):
                counter = 0
                complete = True

        complete = False

        print("humidity completed")
        client.publish("response", json.dumps({
			'task_id': data["task_id"],
			'succeeded': True,
			'humidity' : data_line[0]
        }))
    elif(data["task_type"] == "MC"):#manual control
        #move motor
        #engage humidity
        client.publish("response", json.dumps({
			'task_id': data["task_id"],
			'succeeded': True,
        }))

def on_message1(client, userdata, msg):
    global error_code
    global counter
    instruction = msg.payload.decode('utf-8')
    print(instruction)

    if(instruction != "failed"):
        counter += 1
    else:
    	print("failed to connect, sleeping for 1 second")
    	time.sleep(1)
    	error_code = True
            
    time.sleep(1)
    print(counter)

device = tc.connect('58:82:04:00:09:2E')
tc.powerOn(device)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set('plantCondo', '!9KWdW#egQ7ch8L')
client.connect("84da454f982d4061a3e9339908532687.s1.eu.hivemq.cloud", 8883)
client.subscribe("request")

client1 = mqtt.Client()
client1.on_connect = on_connect1
client1.on_message = on_message1
client1.connect("192.168.0.164", 1883)
client1.subscribe("test/response")
client1.loop_start()
client.loop_forever()
