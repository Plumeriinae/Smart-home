import paho.mqtt.publish as publish # type: ignore

# Define MQTT broker details
broker_ip = "192.168.1.125"
port = 8883
topic = "LED"  # Change this to your desired topic
message = "ON"  # Change this to your desired message

# Publish the message
publish.single(topic, message, hostname=broker_ip, port=port, transport="tcp",retain = True) # websockets

print(f"Message '{message}' published to topic '{topic}' on MQTT broker at {broker_ip}:{port}")
