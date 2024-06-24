from paho.mqtt import client as mqtt_client_lib # type: ignore

import mysql.connector
import random
import datetime, time

import socket

import threading, sys
from pynput import keyboard


#############################################
#!: raspberypi data:
#*: user: pi, password: pi
#*: mysql user: pi, root; password: pi, toor
#!: mqtt ports: 8883(tcp), 8080(wss)
#TODO: DODAJ SECURITY NA MQTT (username, password)
#?: PORABLJENE URE: 26 (preveč)
#############################################

class Mqtt_client():
    def __init__(self, broker: str, port: int, input_topics: list) -> None:
        # Define MQTT broker details
        self.__broker = broker
        self.__port = port
        self.__topics = input_topics
        self.__topics.append("$SYS/broker/clients/connected") #od tega topica dobimo število prijavljenih clientov
        self.number_of_clients = None
        self.client_id = f'mqtt-client-{random.randint(0, 1000)}'
        self.connect_mqtt()
    
    def publish(self, topic:str, message,retain_tmp: bool = False) -> None:
        msg_status = self.client.publish(topic,message,retain = retain_tmp)
        
        if msg_status[0] == 0: #value checking if a message was published successfully
            print(f"Message '{message}' published to topic '{topic}' on MQTT broker at {self.__broker}:{self.__port}")
        else:
            print(f"Failed to send message to topic {topic}")

        if topic not in self.__topics:
            self.__topics.append(topic)
            print("Topic was added to the list of all topics")

    def connect_mqtt(self) -> None: 
        self.client = mqtt_client_lib.Client(client_id=self.client_id, callback_api_version=mqtt_client_lib.CallbackAPIVersion.VERSION2)
        self.client.on_message = on_message
        
        try:
            self.client.connect(self.__broker,self.__port)
        except Exception as e: 
            print(f"Error: {e}")

        for i in self.__topics:
            self.client.subscribe(i)

    def disconnect(self) -> None:
        self.client.disconnect()
    
    def loop(self) -> None:
        self.client.loop_forever(retry_first_connection = True)


#############################################

class mysql_connect():
    def __init__(self) -> None:    
        self.__tbl = "MQTT"
        self.__tbl_clients = "number_of_clients"
        self.__db = "matura"
        __config = {
            'host': 'raspberrypi.local', #TODO: DODAJ DA USER SAM VPIŠE OZ NEK STANDARDEN NASLOV ("raspberrypi.local")
            'port': 3306,
            'user': 'pi',
            'password': 'pi',
            'database': 'matura',
        }
        while True:
            try:
                self.__mydb = mysql.connector.connect(**__config)
                self.__cur = self.__mydb.cursor()
            except Exception as e:
                print(f"Error: {e}")
                try:
                    self.__mydb = mysql.connector.connect(host="192.168.1.150",port=3306,user="pi",password="pi",database="matura")
                    self.__cur = self.__mydb.cursor()
                    if (not self.__mydb.is_connected()):
                        raise ConnectionError
                    else:
                        print("Povezava z DB vzpostavljena")
                        break
                except Exception as x:
                    print(f"Error: {x}")
            if (self.__mydb.is_connected()):
                break
            
    def insert_log(self,topic: str,message) -> None:
        if topic == "$SYS/broker/clients/connected":
            timenow = datetime.datetime.now()
            self.__cur.execute(f"INSERT INTO {self.__tbl_clients} (time,num_of_clients) VALUES ('{timenow}','{message}');") 
            #*: ZA VNOS ŠT CLIENTOV
            print(f"Message was inserted into {self.__db}, {self.__tbl_clients}. Message was {message}, on topic: {topic}, with time {timenow}\n")
            self.__mydb.commit()
            #*: TABELA: "number_of_clients", ATRIBUTI: "time, num_of_clients"
        
        else:
            self.__cur.execute(f"INSERT INTO {self.__tbl} (topic,message) VALUES ('{topic}','{message}');") 
            #*: ZA VNOS STATUSA LUČKE OZ DRUGIH STVARI GLEDE NA TOPIC (SENZORJI, LED, MOTORČEK)
            print(f"Message was inserted into {self.__db}, {self.__tbl}. Message was {message}, on topic: {topic} \n")
            self.__mydb.commit()
            #*: TABELA: "MQTT", ATRIBUTI: "topic,message"
    
    def query(self,statement) -> list: #* lahko kličemo query 
        self.__cur.execute(statement)
        result = self.__cur.fetchall()
        return result
    
    def disconnect(self) -> None:
        self.__cur.close()
        self.__mydb.close()



#############################################

#! NE RABIMO
class LoggingSystem(): 
    #TODO mogoče dodamo da shranjujemo errorje v Loge(nek file).
    pass

#############################################

#! NE RABIMO
class GetClients(): 
    #TODO: MOGOČE DODAMO DA DOBIMO TOČNE CLIENTE KI SO POVEZANI
    pass

#############################################

#! NE RABIMO
class get_connections(): #* za GetClients class pripravljeno
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0",25562))
        s.listen(5)
    
    #?: KAKO NAREDITI DA IMAMO DVE RAZLIČNI POVEZAVI NA ISTI SERVER NA ARDUINO
    #?: MOGOČE MULTITHREDING??

#############################################

#! ne vnesi vsakič ko se spremeni število clietov
def on_message(client, userdata, msg):
    msg_decoded = msg.payload.decode()
    
    try:
        mydb_conn.insert_log(msg.topic,msg_decoded)
        print(f"Msg: {msg_decoded}, Topic:{msg.topic}")
    except Exception as e:
        print(f"Error: {e}")

#############################################

if __name__ == '__main__': 
    try:
        mqtt_conn = Mqtt_client("192.168.1.125", 8883, ["LED","FAN","MOVEMENT","TEMPERATURA","SERVER"])
        mqtt_conn.publish("SERVER","RUNNING")
        
        global mydb_conn
        mydb_conn = mysql_connect()
        try:
            mqtt_conn.loop()
        except KeyboardInterrupt as e:
            print(f"Error: KeyboardInterrupt")
        except Exception as e:
            print(f"Error: {e}")
    finally:
        mqtt_conn.publish("SERVER","STOPPED")
        mqtt_conn.disconnect()
        
        mydb_conn.disconnect()
        #// mqtt_conn.publish(topic,msg)