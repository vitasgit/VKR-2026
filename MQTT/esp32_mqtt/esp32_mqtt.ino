#include <WiFi.h>
//#include "WiFi.h"
#include <PubSubClient.h>

// !!!!! для  ТЕСТА !!!!!!!!!!!!!!!!!!
const char* ssid = "RTK-26-2";
const char* password = "77450145255";
IPAddress ip_orange(192, 168, 0, 18);   // 4 байта

WiFiClient espClient;
PubSubClient client(espClient);
uint8_t led = 2;

void callback(char* topic, byte* payload, unsigned int length) {
  if (length == 0) {return;}  // проверка на пустые сообщения

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if ((char)payload[0] == '1') {
    digitalWrite(led, HIGH);
  } 
  else if ((char)payload[0] == '0') {
    digitalWrite(led, LOW);
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
    if (client.connect(clientId.c_str(), "vitaly", "123456")) {  // id, [имя_юзера, пароль] - пользователь из passwd
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
  pinMode(led, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("wifi...");
  }
  Serial.println(WiFi.localIP());

  client.setCallback(callback);
  //client.setClient(espClient);
  client.setServer(ip_orange, 1883);  // ip сервера и порт

}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // обработка клиента

}
