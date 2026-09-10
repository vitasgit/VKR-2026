#include "WiFi.h"
#include "myPasswords.h"

// ------------!!!! пароли ак---------------
const char* ssid = MY_SSID;
const char* password = MY_PASSWORD;

int ledPin = 2;

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

  digitalWrite(ledPin, HIGH);
}

void loop() {
  while (WiFi.status() != WL_CONNECTED) { delay(1000); WiFi.begin(ssid, password);}

  digitalWrite(ledPin, LOW);
  delay(1000);
  digitalWrite(ledPin, HIGH);
  delay(1000);
}
