#include "WiFi.h"
#include "myPasswords.h"
#include <PubSubClient.h>

// ------------!!!! пароли ---------------
const char* ssid = MY_SSID;
const char* password = MY_PASSWORD;

int ledPin = 2;

// WiFiServer EspServer(80);  // HTTP
IPAddress ip_orange(192, 168, 0, 18);   // 4 байта
WiFiClient espClient;  // TCP/IP
PubSubClient client(espClient);  // указываем в качестве парам, на каком стеке/протоколе будет связь

void callback(char* topic, byte* payload, unsigned int length) {
  if (length == 0) {return;}  // проверка на пустые сообщения


  char strCmd[length+1];
  memcpy(strCmd, payload, length);
  strCmd[length] = '\0';

  if (strcmp(strCmd, "ledOn") == 0) {
    digitalWrite(ledPin, HIGH);
    Serial.println(strCmd);
  } 
  else if (strcmp(strCmd, "ledOff") == 0) {
    digitalWrite(ledPin, LOW);
    Serial.println(strCmd);
  }
  else {Serial.println("ошибка передачи mqtt");}

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "espClient-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    // boolean connect (clientID, [username, password], [willTopic, willQoS, willRetain, willMessage], [cleanSession])
    if (client.connect(clientId.c_str(), "vitaly", "123456")) {  // id, [имя_юзера, пароль] - пользователь из passwd, mqtt server
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("home/led");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("...");
  }

  Serial.println(WiFi.localIP());
  client.setCallback(callback);
  client.setServer(ip_orange, 1883);  // ip сервера и порт, mqtt server
  //EspServer.begin();  // HTTP

  digitalWrite(ledPin, HIGH);

  //char[256] data;
}

void loop() {
  
  // mqtt server
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // обработка клиента
  
  
  // передача по HTTP
  /*
  WiFiClient client = EspServer.available();

  if (client) {
    String request = client.readString();  // readString ждет 1с. Альтернатива -  readStringUntil('\n')

    if (request.indexOf("GET /?command=1") != -1) {
      Serial.write('1');
      digitalWrite(ledPin, HIGH);
      client.println("HTTP/1.1 200 OK");
      client.println();
    }
    else if (request.indexOf("GET /?command=0") != -1) {
      Serial.write('0');
      digitalWrite(ledPin, LOW);
      client.println("HTTP/1.1 200 OK");
      client.println();
    }

    client.stop();
  }
  */
}
