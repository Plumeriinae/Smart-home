var clientId = "clientID - "+parseInt(Math.random() * 100); // Configure MQTT broker details

var client = new Paho.Client("192.168.1.125",Number(8080), clientId); // Create a client instance
const topics = ["LED","FAN","MOVEMENT","TEMPERATURA","$SYS/broker/clients/connected","SERVER"];
client.onConnectionLost = onConnectionLost; // Set callback functions
client.onMessageArrived = onMessageArrived; // Set callback functions

// Connect to the broker
client.connect({            
    onSuccess: onConnect,
});

// Function to handle successful connection
function onConnect() {
    console.log('Connected to MQTT broker');
    console.log(clientId);

    topics.forEach (tpc => 
        client.subscribe(tpc),
    );
}

// Function to handle connection loss
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.error('Connection lost: ' + responseObject.errorMessage);
    }
}

// Function to handle incoming messages
function onMessageArrived(message) {
    console.log('Received message: ' + message.payloadString);
    switch (message.topic) {
        case ("TEMPERATURA"):
            document.getElementById("temp").innerHTML = "<span>"+ message.payloadString + "°C"+"</span>";
            break;
        case ("$SYS/broker/clients/connected"):
            document.getElementById("cli").innerHTML = "<span>"+ message.payloadString + "</span>";
            break;
        case ("SERVER"):
            document.getElementById("serv").innerHTML = "<span>"+message.payloadString + "</span>";
            break;
    }
}

// Function to send an MQTT message
function turnOnLED() {
    var message = new Paho.Message('ON');
    message.destinationName = "LED";
    message.retained = true;
    client.send(message);
}

function turnOffLED() {
    var message = new Paho.Message('OFF');
    message.destinationName = "LED";
    message.retained = true;
    client.send(message);
}

function serverON() {
    var message = new Paho.Message('RUNNING');
    message.destinationName = "SERVER";
    message.retained = true;
    client.send(message);
}

function ServerOFF() {
    var message = new Paho.Message('STOPPED');
    message.destinationName = "SERVER";
    message.retained = true;
    client.send(message);
}