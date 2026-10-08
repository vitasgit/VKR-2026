from RF24 import RF24, RF24_PA_LOW, RF24_250KBPS, RF24_DRIVER
#import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client


rf24_ard = RF24(73, 11)  # (ce_pin, csn_pin)
pipe1_addr = b"1Node"  # [49, 78, 111, 100, 101]

def init_rf24():
    if not(rf24_ard.begin()):
        return False
    
    rf24_ard.setPALevel(RF24_PA_LOW)        # мощность передатчика (low = -12 dBm)
    rf24_ard.setDataRate(RF24_250KBPS)      # Скорость передачи данных, чем меньше - тем дальше (скорость приема и передачи должна быть одинаковая)
    rf24_ard.setAutoAck(1);                 # режим подтверждения приёма, 1 вкл 0 выкл
    rf24_ard.setRetries(0, 15);             # (время между попыткой достучаться, число попыток) 15 - максимальное
    rf24_ard.setPayloadSize(1);             # пакет данных размером 1 байт (бубу передавать 1 или 0)
    rf24_ard.setChannel(76)                 # выбираем канал передачи данных с самыми низкими помехами
    rf24_ard.powerUp();                     # режим передачи (повышенного потребления), powerDown - режим ожидания
    rf24_ard.openWritingPipe(pipe1_addr);   # открыть канал на отправку
    rf24_ard.stopListening()                # режим передачи

    return True





def mqtt_connect():
    # Client.on_connect
    def mqtt_reconnect(mqttClient, userdata, flags, reason_code, properties=None):
        if reason_code == 0: print("подключен radio_mqtt")
        else: print(f"ошибка: {reason_code}")
        mqttClient.subscribe(topic="home/air/cmd")

    # client.on_message
    # mqttmessage - class paho.mqtt.client.MQTTMessage
    def mqtt_message(mqttClient, userdata, mqttmessage):
        data = str(mqttmessage.payload, encoding='utf-8')  # байты payload --> тип str
        print(data)
        if (send_rf24(data) == True):
            mqttClient.publish(topic="home/air/state",
                                payload=data,
                                qos=0,  # без подтверждений
                                retain=True  # брокер передаст контроллеру последнее отправленное сообщение (если контроллер вырубит, то ему будет отправлено посл сообщение)
                               )
        else: print("ошибка - send_rf24 !!!!!!!")
            
        
    
    # создаю объект mqttClient типа mqtt_client.Client(). paho.mqtt.client
    # help(mqtt_client.Client)
    mqttClient = mqtt_client.Client(
        client_id="id_radio",
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )

    mqttClient.username_pw_set("vitaly", "123456")
    mqttClient.on_connect = mqtt_reconnect
    mqttClient.on_message = mqtt_message
    mqttClient.connect(host="localhost", port=1883, keepalive=60)  # каждые 60 сек шлем на сервер ping живности
    
    # проверка на connect. is_connected() → bool

    return mqttClient

    


def send_rf24(cmd):
    # проверка что команда корректная
    # ...
    if cmd == "1": data = b"\x01"
    elif cmd == "0": data = b"\x00"
    else:
        print("неправильная команда")
        return

    ## adwd
    res = False
    try:
        res = rf24_ard.write(data)
    except:
        print("ошибка")

    return res



if __name__ == '__main__':
    if (init_rf24() == False):
        print("rf24 не работает")
        # exit()
    
    # обработка случая, когда служба mosquitto выключена
    # reconnect как в esp32
    mqttClient = mqtt_connect()
    # print("mqttClient.is_connected() == ", mqttClient.is_connected())
    mqttClient.loop_forever()
