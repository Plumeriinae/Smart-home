from paho.mqtt import client as mqtt_client_lib 

import mysql.connector
import random
import datetime, time

import os


#############################################
#!: raspberypi data:
#*: user: pi, password: pi
#*: mysql user: pi, root; password: pi, toor
#!: mqtt ports: 8883(tcp), 8080(wss)
#TODO: DODAJ SECURITY NA MQTT (username, password)
#?: PORABLJENE URE: 31 (preveč)
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
        global count
        msg_status = self.client.publish(topic,message,retain = retain_tmp)
        
        if msg_status[0] == 0: #value checking if a message was published successfully
            print(f"{count}\\\MQTT-Tx\\\ [Published message: '{message}'; Topic: '{topic}'; Retain: {retain_tmp}; MQTT broker: {self.__broker}:{self.__port}]\n")
            count += 1
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
            filelog(e,"MQTT")

        for i in self.__topics:
            self.client.subscribe(i)

    def disconnect(self) -> None:
        self.client.disconnect()
    
    def loop(self) -> None:
        self.client.loop_forever()


#############################################

class mysql_connect():
    def __init__(self) -> None:    
        self.__tbl = "MQTT"
        self.__tbl_clients = "number_of_clients"
        self.__db = "matura"
        __config = {
            'host': 'raspberrypi.local',
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
                filelog(x,"MYSQL-connections")
                try:
                    self.__mydb = mysql.connector.connect(host="192.168.1.150",
                        port=3306,
                        user="pi",
                        password="pi",
                        database="matura")
                    self.__cur = self.__mydb.cursor()
                    if (not self.__mydb.is_connected()):
                        raise ConnectionError
                    else:
                        print("Povezava z DB vzpostavljena")
                        break
                except Exception as x:
                    print(f"Error: {x}")
                    filelog(x,"MYSQL-connections-2nd-ip")
                    break
            if (self.__mydb.is_connected()):
                break
            
    def insert_log(self,topic: str,message) -> None:
        global count
        if topic == "$SYS/broker/clients/connected":
            timenow = datetime.datetime.now()
            self.__cur.execute(f"INSERT INTO {self.__tbl_clients} (time,num_of_clients) VALUES ('{timenow}','{message}');") 
            #*: ZA VNOS ŠT CLIENTOV
            log = f"{count}\\\MSQL-Tx\\\ [Inserted in: {self.__db}, {self.__tbl_clients}. Message: {message}; Topic: {topic}; Time: {timenow}]\n"
            filelog(log); print(log)
            count += 1
            self.__mydb.commit()
            #*: TABELA: "number_of_clients", ATRIBUTI: "time, num_of_clients"
        
        else:
            self.__cur.execute(f"INSERT INTO {self.__tbl} (topic,message) VALUES ('{topic}','{message}');") 
            #*: ZA VNOS STATUSA LUČKE OZ DRUGIH STVARI GLEDE NA TOPIC (SENZORJI, LED, MOTORČEK)
            log = f"{count}\\\MSQL-Tx\\\ [Inserted in: {self.__db}, {self.__tbl_clients}. Message: {message}; Topic: {topic}]\n"
            filelog(log); print(log)
            count += 1
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

def on_message(client, userdata, msg):
    msg_decoded = msg.payload.decode()
    global count
    if not msg.retain: # da ne vnašamo starih mqtt mssagov v db
        try:
            log = f"{count}\\\MQTT-Rx\\\ [Topic:{msg.topic}, Content: {msg_decoded}, Retained: {msg.retain}]"
            print(log); filelog(log)
            mydb_conn.insert_log(msg.topic,msg_decoded)
        except Exception as e:
            print(f"Error: {e}")
            filelog(e,"MQTT-message")
    
    elif msg.topic == "$SYS/broker/clients/connected":
        try:
            log = f"{count}\\\MQTT-Rx\\\ [Topic:{msg.topic}, Content: {msg_decoded}, Retained: {msg.retain}]"
            print(log); filelog(log)
            mydb_conn.insert_log(msg.topic,msg_decoded)
        except Exception as e:
            print(f"Error: {e}")
            filelog(e,"MQTT-message")

#############################################
def filelog(data,location: str = None):
    if location == None:
        with open("logs-server.txt","a") as fh:
            fh.write(f"{data}\n")
    else:
        with open("errors-server.txt","a") as fh:
            fh.write(f"Error: {data}, in: {location}\n")
#############################################

if __name__ == '__main__':
    if os.path.isfile("log-server.txt"):
        os.remove("log-server.txt")
    if os.path.isfile("errors-server.txt"):
        os.remove("errors-server.txt")
    
    try:
        global count
        count = 1

        mqtt_conn = Mqtt_client("192.168.1.125", 8883, ["LED","FAN","MOVEMENT","TEMPERATURA","SERVER"])
        if mqtt_conn != None:
            mqtt_conn.publish("SERVER","RUNNING",True)
        
        mydb_conn = mysql_connect()
        try:
            mqtt_conn.loop()
        except KeyboardInterrupt as e:
            print(f"Error: KeyboardInterrupt")
        except Exception as e:
            print(f"Error: {e}")
            filelog(e,"MQTT-loop")
    except Exception as e:
        print(f"Error: {e}")
        filelog(e,"Main function")

    finally:
        mqtt_conn.publish("SERVER","STOPPED",True)
        mqtt_conn.disconnect()
        
        mydb_conn.disconnect()

