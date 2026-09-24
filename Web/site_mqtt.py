from flask import Flask, render_template, request
from RF24 import RF24, RF24_PA_LOW, RF24_250KBPS, RF24_DRIVER
import time, requests
#import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client

ESP_IP= "http://192.168.0.13";
app = Flask(__name__)

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


def send_esp32(cmd):
    # проверка что команда корректная
    # ...
    url = f"{ESP_IP}/?command={cmd}"
    print(url)

    ## сделать более подробный вывод ошибок
    try:
        requests.get(url, timeout=2)
    except:
        print("ошибка")


def send_esp32_mqtt_single(cmd):
    # print(publish.single.__doc__)
    publish.single(topic="home/led",
                   payload=cmd,
                   qos=0,
                   hostname="localhost",
                   port=1883,
                   auth={'username':"vitaly", 'password':"123456"}
                   )


def mqtt_connect():
    # создаю объект client типа mqtt_client.Client(). paho.mqtt.client
    # help(mqtt_client.Client)
    client = mqtt_client.Client(
        client_id="id123",
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )

    # client.username_pw_set("vitaly", "123456")
    client.connect(host="localhost", port=1883, keepalive=60)  # каждые 60 сек шлем на сервер ping живности

    return client


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



@app.route("/", methods=["POST", "GET"])
def index():    
    return render_template('index.html')


@app.route("/esp32", methods=["POST", "GET"])
def toESP32():
    if request.method == "POST":
        cmd = request.form.get('esp32')   # обращаемся к полю submit (name="submit")
        #print(request.form.get('submit'))

        #send_esp32(cmd)  # HTTP
        # send_esp32_mqtt(cmd)  # mqtt
        client.publish(topic="home/led",
                   payload=cmd,
                   qos=1,
                   retain=True  # брокер передаст контроллеру последнее отправленное сообщение (если контроллер вырубит, то ему будет отправлено посл сообщение)
                   )
        # сделать проверку что ф-ция сработала как в RF24
        #if (send_esp32(cmd)): print("ОК")

    
    return render_template('index.html')


@app.route("/RF24", methods=["POST", "GET"])
def toRF24():
    if request.method == "POST":
        cmd = request.form.get('RF24')   # обращаемся к полю submit (name="submit")

        if send_rf24(cmd): print("RF24 - OK")
        else:
            print("RF24 - не передает!!!!!")
            #exit()  ## !! ошибка
    
    return render_template('index.html')


if __name__ == '__main__':
    if (init_rf24() == False):
        print("rf24 не работает")
        exit()

    client = mqtt_connect()
    client.loop_start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
