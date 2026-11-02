#include "WiFi.h"
#include "myPasswords.h"
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ------------!!!! пароли ---------------
const char* ssid = MY_SSID;
const char* password = MY_PASSWORD;

int ledPin = 2;

// WiFiServer EspServer(80);  // HTTP
// IPAddress ip_orange(192, 168, 0, 101);   // 4 байта дома статика
IPAddress ip_orange(192, 168, 43, 78);   // 4 байта телефон технопарк
WiFiClient wifiClient;  // TCP/IP
PubSubClient mqttClient(wifiClient);  // указываем в качестве парам, на каком стеке/протоколе будет связь

// https://pubsubclient.knolleary.net/api#publish
void toBroker(char* state)
{
  mqttClient.publish("home/led/state",  // topic const char[]
                     state,  // payload const char[], byte[] - две функции/перезагрузки. для строк длина не нужна
                     //sizeof(val),  // length unsigned int
                     true  // retained boolean (optional)
  );
}

void callback(char* topic, byte* payload, unsigned int length)
{
  if (length == 0) {return;}  // проверка на пустые сообщения

  // обработать json ответ от сервера
  // ...
  char strCmd[length+1];
  memcpy(strCmd, payload, length);
  strCmd[length] = '\0';

  if (strcmp(strCmd, "ledOn") == 0) {
    digitalWrite(ledPin, HIGH); toBroker("ON");
    Serial.println(strCmd);
  }
  else if (strcmp(strCmd, "ledOff") == 0) {
    digitalWrite(ledPin, LOW); toBroker("OFF");
    Serial.println(strCmd);
  }
  else {Serial.println("ошибка передачи mqtt");}

}

void reconnect()
{
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String deviceId = "espID-";
    deviceId += String(random(0xffff), HEX);
    // Attempt to connect
    // boolean connect (deviceId, [username, password], [willTopic, willQoS, willRetain, willMessage], [cleanSession])
    if (mqttClient.connect(deviceId.c_str(), "vitaly", "123456")) {  // id, [имя_юзера, пароль] - пользователь из passwd, mqtt server
      Serial.println("connected");
      // Once connected, publish an announcement...
      //mqttClient.publish("outTopic", "hello world");
      // ... and resubscribe
      mqttClient.subscribe("home/devices/<clientId>/cmd");  // Как прописать ID устройства?
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println("try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// запрос на сервер
void req_json()
{
  // Allocate the JSON document
  JsonDocument data;
  data["name"] = "esp-диод";
  data["type"] = "switch";
  data["command"] = "ON";
  data["status"] = true;
  data["error"] = 0;

  serializeJson(data, Serial);
}

void setup()
{
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("...");
  }

  Serial.println(WiFi.localIP());
  mqttClient.setCallback(callback);
  mqttClient.setServer(ip_orange, 1883);  // ip сервера и порт, mqtt server
  //EspServer.begin();  // HTTP
  Serial.println("mqtt server...");

  digitalWrite(ledPin, HIGH);

  //char[256] data;
}

void loop()
{

  // mqtt server
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();  // обработка клиента


  // передача по HTTP
  /*
   *  WiFiClient client = EspServer.available();
   *
   *  if (client) {
   *    String request = client.readString();  // readString ждет 1с. Альтернатива -  readStringUntil('\n')
   *
   *    if (request.indexOf("GET /?command=1") != -1) {
   *      Serial.write('1');
   *      digitalWrite(ledPin, HIGH);
   *      client.println("HTTP/1.1 200 OK");
   *      client.println();
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
