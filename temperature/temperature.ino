#include <Ethernet.h>


const int BAUD_RATE = 9600;

// username pi
// pass pi
// root pass toor
const char* RPI_SERVER = "192.168.1.100"; //"raspberrypi.local";  Lahko se tudi uporabi str"(String)"
const int RPI_PORT = 12345;

const int SENSOR_IN_PIN = A1;

EthernetClient client;  //razred EthernetClient

byte MAC[] = {
  0x00, 0xAA, 0xBB, 0xCC, 0xDE, 0x02
};

int BlueLED = 6;
int GreenLED = 7;
int RedLED = 8;

void setup() {
  Serial.begin(BAUD_RATE);

  Serial.println("Initialize Ethernet with DHCP.");
  while (Ethernet.begin(MAC) == 0) {      //pošlje zahtevo za ip preko dhcp
    Serial.println("Failed to configure Ethernet using DHCP");
  }

  Serial.print("My IP address: ");      //izpiše na usb
  Serial.println(Ethernet.localIP());

  pinMode(SENSOR_IN_PIN, INPUT);
  pinMode(BlueLED, OUTPUT);
  pinMode(GreenLED, OUTPUT);
  pinMode(RedLED, OUTPUT);
}

void loop() {
  int data = analogRead(SENSOR_IN_PIN);
  float voltage = data*5.0;
  voltage /= 1024.0;

  float temp = (voltage - 0.5) * 100 ;

  if (temp < 24) {
  digitalWrite(BlueLED, HIGH);
  digitalWrite(GreenLED, LOW);
  digitalWrite(RedLED, LOW);
  }

  if (temp < 26 and temp > 24) {
  digitalWrite(BlueLED, LOW);
  digitalWrite(GreenLED, HIGH);
  digitalWrite(RedLED, LOW);
  }

  if (temp > 26){
  digitalWrite(BlueLED, LOW);
  digitalWrite(GreenLED, LOW);
  digitalWrite(RedLED, HIGH);
  }

  if (!client.connected()) {  // <-
    //reconnect 
    int conn_status = client.connect(RPI_SERVER, RPI_PORT); // <-

    if (!client.connected()) {
      Serial.println("Connection to " + (String)RPI_SERVER + " failed.");
      Serial.println("Return code: " + (String)conn_status);
    }
    } 
  else {
    client.print(String(temp)); // <- 
    }
  Serial.print(temp); Serial.println("°C");

  delay(2500);
}
