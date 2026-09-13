#include <SPI.h>
#include <RF24.h>

/*
https://rf24.readthedocs.io/en/v1.4.4/classRF24.html#_CPPv44RF24
https://nrf24.github.io/RF24/md_docs_2arduino.html
*/

RF24 rf24_ard(9, 10);  // (ce_pin, csn_pin) (зеленый, синий)

// строго 5 байт на имя, адрес трубы (pipe)
/*
Pipes 1-5 should share the same address, except the first byte. 
Only the first byte in the array should be unique, e.g.
*/
uint8_t pipe1_addr[5] = {"1Node"};

void setup() {
  pinMode(7, OUTPUT);
  Serial.begin(115200);

  // распиновка по документации arduino uno
  // можно так же использовать ICSP интерфейс
  //SPI.setMOSI(11);  // корич
  //SPI.setMISO(12);  // белый
  //SPI.setSCK(13);   // бордовый                       !!!!!!!!!!!!!! 13 pin занят. !!!

  if (!rf24_ard.begin()) {
    Serial.println("rf24 не работает");
    return;
  }

  rf24_ard.setPALevel(RF24_PA_LOW);
  rf24_ard.setDataRate(RF24_250KBPS);
  rf24_ard.setChannel(76);
  // попробовать сделать 32 и пересылать 1.
  rf24_ard.setPayloadSize(1);  // размер пакета (полезной нагрузки) - 1 байт (1 или 0). макс 32
  rf24_ard.openReadingPipe(0, pipe1_addr);
  rf24_ard.startListening();

  Serial.print("OK RF24");
  digitalWrite(7, HIGH);
  delay(500);
  digitalWrite(7, LOW);
  delay(500);

}

void loop() {
  uint8_t data;
  if(rf24_ard.available()){
    rf24_ard.read(&data, 1);  // читать 1  байт(setPayloadSize). макс - 32

    if (data == 1) {
      digitalWrite(7, HIGH);
      Serial.println(data);
    }
    else if (data == 0) {
      digitalWrite(7, LOW);
      Serial.println(data);
    }
    else {
      Serial.println("ошибка передачи");
    }
  }


}
