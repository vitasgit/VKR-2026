from flask import Flask, render_template, request
import time, requests, json
#import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client

app = Flask(__name__)

def send_esp32_mqtt(cmd):
    # проверка что команда корректная
    # ...
    
    mqttClient.publish(topic="home/led",
                   payload=cmd,
                   qos=0,  # без подтверждений
                   retain=True  # брокер передаст контроллеру последнее отправленное сообщение (если контроллер вырубит, то ему будет отправлено посл сообщение)
                   )
    # return True если успешно выполнился client.publish()



def mqtt_connect():
    # Client.on_connect
    def mqtt_reconnect(mqttClient, userdata, flags, reason_code, properties=None):
        if reason_code == 0: print("подключен mqtt")
        else: print(f"ошибка: {reason_code}")
        mqttClient.subscribe(topic="home/led/state")

    # client.on_message
    # mqttmessage - class paho.mqtt.client.MQTTMessage
    def mqtt_message(mqttClient, userdata, mqttmessage):
        print(str(mqttmessage.payload, encoding='utf-8'))  # байты payload --> тип str
        
    
    # создаю объект mqttClient типа mqtt_client.Client(). paho.mqtt.client
    # help(mqtt_client.Client)
    mqttClient = mqtt_client.Client(
        client_id="id123",
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )

    mqttClient.username_pw_set("vitaly", "123456")
    mqttClient.on_connect = mqtt_reconnect
    mqttClient.on_message = mqtt_message
    mqttClient.connect(host="localhost", port=1883, keepalive=60)  # каждые 60 сек шлем на сервер ping живности
    
    # проверка на connect. is_connected() → bool

    return mqttClient


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template('index.html')


@app.route("/esp32", methods=["POST", "GET"])
def toESP32():
    if request.method == "POST":
        cmd = request.form.get('esp32')   # обращаемся к полю submit (name="submit")
        #print(request.form.get('submit'))

        #send_esp32(cmd)  # HTTP
        send_esp32_mqtt(cmd)  # mqtt
        # сделать проверку что ф-ция сработала как в RF24
        #if (send_esp32(cmd)): print("ОК")

    
    return render_template('index.html')


@app.route("/RF24", methods=["POST", "GET"])
def toRF24():
    if request.method == "POST":
        cmd = request.form.get('RF24')   # обращаемся к полю submit (name="submit")
        mqttClient.publish(topic="home/air/cmd",
                   payload=cmd,
                   qos=0,  # без подтверждений
                   retain=True  # брокер передаст контроллеру последнее отправленное сообщение (если контроллер вырубит, то ему будет отправлено посл сообщение)
                   )
    return render_template('index.html')


# Получаем запрос от Яндекса и возвращаем ответ
# req - запрос от яндекса
# подробнее в доке: https://yandex.ru/dev/dialogs/alice/doc/ru/response
# пример: https://github.com/yandex/alice-skills/blob/master/python/buy-elephant/now/api.py
@app.route("/alice/SECRET_URL", methods=["POST"])
def handle_yandex():
    req = request.json
    print(req)

    # ответ яндексу
    res = {
        "response": {
            "text": "Включаю свет",  # !! баг
            "end_session": False
        },
        "version": "1.0"
    }

    # Обрабатываем ответ пользователя
    # original_utterance - Полный текст пользовательского запроса, максимум 1024 символа
    # command - нормализованный текст запроса
    # нет проверки на случай если command в запросе нет

    # new - boolean, если true, то сессия новая
    if (req['session']['new']): res['response']['text'] = 'Привет! Я умею только включать и выключать свет'  # !! баг
    if ("включи" in req["request"]["command"] and
        "свет" in req["request"]["command"]
        ):
        res['response']['text'] = 'Включаю свет'
        send_esp32_mqtt("ledOn")

    elif ("выключи" in req["request"]["command"] and
        "свет" in req["request"]["command"]
        ):
        res['response']['text'] = 'Выключаю'
        send_esp32_mqtt("ledOff")

    else:
        res['response']['text'] = 'Не поняла. Я умею только включать и выключать свет'

    return json.dumps(
        res,
        ensure_ascii=False,  # поддержка русского
        indent=2  # два пробела
        )

    

if __name__ == '__main__':    
    # обработка случая, когда служба mosquitto выключена
    # reconnect как в esp32
    mqttClient = mqtt_connect()
    # print("mqttClient.is_connected() == ", mqttClient.is_connected())
    mqttClient.loop_start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
