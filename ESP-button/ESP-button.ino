#include <Ethernet.h>
#include <PubSubClient.h>


const char* server = "192.168.1.125";
const int mqtt_port = 8883;
const char* mqtt_topic = "LED/0";
const char* mqtt_topic_druga = "LED/1";
const char* mqtt_topic_temp = "TEMPERATURA";
const char* clientName = "Arduino5000";

//COM4 luc + gumb / 0 - zgornji
//COM3 luc + temp / 1 - spodnji


// pins
const int ledPin = 6;
const int motorPin = 7;
const int buttonPin = 8;
const int sensorPin = 9;
const char turn_on[] = "ON";
const char turn_off[] = "OFF";

bool LedState = LOW;

int timeStart = millis();
int timeNow = millis();


EthernetClient ethClient;
PubSubClient client(ethClient);

void setup() {
  Serial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin,OUTPUT);
  pinMode(motorPin,OUTPUT);
  pinMode(sensorPin,INPUT);

  // Initialize Ethernet
  randomSeed(analogRead(0));
  byte mac[] = {0xDE, 0xAD, 0xA5, 0x78, 0x5D, 0x25};
  Ethernet.begin(mac);

  client.setServer(server, mqtt_port);
  client.setCallback(callback);

  // povezemo na MQTT broker
  reconnect();
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  bool ButtonState = digitalRead(buttonPin);
  
  if (LedState == LOW && ButtonState == LOW) {
    Serial.println("LED on button");
    client.publish(mqtt_topic, turn_on, true);
    client.publish(mqtt_topic_druga, turn_on, true);
    LedState = HIGH;
    delay(500);
  }
  
  else if (LedState == HIGH && ButtonState == LOW) {
        client.publish(mqtt_topic, turn_off, true);
        client.publish(mqtt_topic_druga, turn_off, true);
        Serial.println("LED off button");
        LedState = LOW;
        delay(500);
  }
  if (mqtt_topic == "LED/1") {
    timeNow = millis();
    if (timeNow - timeStart >= 10000) {
      temp();
      timeStart = millis();
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // incoming MQTT messages
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  if (String(topic) == String(mqtt_topic)) {
    if (message == "ON") { //  ter odstrani "String()""
      digitalWrite(ledPin, HIGH);
      Serial.print("ON \n");
    } else if (message == "OFF") {
      digitalWrite(ledPin, LOW);
      Serial.print("OFF \n");
    }
  }
  if (String(topic) == "FAN") {
    if (message == "ON") { //  ter odstrani "String()""
      digitalWrite(motorPin, HIGH);
      Serial.print("ON \n");
    } else if (message == "OFF") {
      digitalWrite(motorPin, LOW);
      Serial.print("OFF \n");
    }
  }
}

void reconnect() { 
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(clientName)) {
      Serial.println("connected");
      client.subscribe(mqtt_topic);
      client.subscribe("FAN"); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void temp() {
  int data = analogRead(sensorPin);
  char char_temp[4];
  dtostrf(data, 6, 2, char_temp);
  char_temp[2] = LOW;
  client.publish(mqtt_topic_temp, char_temp, true);
  Serial.print("Temperatura: ");
  Serial.print(data);
  Serial.print('\n');
}