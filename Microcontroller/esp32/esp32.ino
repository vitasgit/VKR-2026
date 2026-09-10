#include "WiFi.h"
#include "myPasswords.h"

// ------------!!!! пароли ---------------
const char* ssid = MY_SSID;
const char* password = MY_PASSWORD;

int ledPin = 2;

WiFiServer EspServer(80);  // HTTP
void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("...");
  }

  Serial.println("IP: ");
  Serial.println(WiFi.localIP());
  EspServer.begin();

  digitalWrite(ledPin, HIGH);

  //char[256] data;
}

void loop() {
  WiFiClient client = EspServer.available();

  if (client) {
    String request = client.readString();

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
}
