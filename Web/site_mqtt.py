from flask import Flask, render_template, request
import time, requests, json
#import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt_client

# для генерации html
from jinja2 import Template

app = Flask(__name__)
devices = {}
lives = {}
scenaries = {}

def toDevice(device_id, cmd):
    # проверка что команда корректная
    # ...
    command = {"value": cmd}
    js_payload = json.dumps(
        command,
        ensure_ascii=False,  # поддержка русского
        indent=2  # два пробела
        )
    mqttClient.publish(topic=f"home/devices/{device_id}/cmd",
                       payload=js_payload,
                       qos=0,  # без подтверждений
                       retain=True  # брокер передаст контроллеру последнее отправленное сообщение (если контроллер вырубит, то ему будет отправлено посл сообщение)
                       )
    # return True если успешно выполнился client.publish()


def check_scen(dev, val):
    for i in scenaries:
        s = scenaries[i]
        
        if s["if_dev"] == dev:
            if s["oper"] == "==":
                if str(s["if_val"]) == str(val): toDevice(s["then_dev"], s["then_cmd"])
            elif s["oper"] == "<":
                if float(val) < float(s["if_val"]): toDevice(s["then_dev"], s["then_cmd"])
            elif s["oper"] == ">":
                if float(val) > float(s["if_val"]): toDevice(s["then_dev"], s["then_cmd"])


def handle_json(topic, payload):
    arr = topic.split("/")
    dev = arr[2]  # id, имя устройства
    
    try:
        data = json.loads(payload)
        devices[dev] = data
        check_scen(dev, data["value"])
        # print("json data= ", data)
        print("devices:")
        print(devices)
    except:
        print("ошибка обработки payload json")


def handle_live(topic, payload):
    arr = topic.split("/")
    dev = arr[2]
    lives[dev] = payload

    
def mqtt_connect():
    # Client.on_connect
    def mqtt_reconnect(mqttClient, userdata, flags, reason_code, properties=None):
        if reason_code == 0: print("подключен mqtt")
        else: print(f"ошибка: {reason_code}")
        mqttClient.subscribe(topic="home/devices/+/state")
        mqttClient.subscribe(topic="home/devices/+/live")

    # client.on_message
    # mqttmessage - class paho.mqtt.client.MQTTMessage
    def mqtt_message(mqttClient, userdata, mqttmessage):
        payload = str(mqttmessage.payload, encoding='utf-8')  # байты payload --> тип str
        # print(payload)

        arrTopic = mqttmessage.topic.split("/")
        if (arrTopic[-1] == "live"): handle_live(mqttmessage.topic, payload) 
        else: handle_json(mqttmessage.topic, payload)
        
    
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
    return render_template('index.html', devices=devices, lives=lives, scenaries=scenaries)  # передаем словарь devices в переменную devices


@app.route("/device", methods=["POST", "GET"])
def device():
    if request.method == "POST":
        cmd = request.form.get('cmd')   # обращаемся к полю submit (name="cmd")
        device_id = request.form.get('device_id')
        #print(request.form.get('submit'))

        #send_esp32(cmd)  # HTTP
        toDevice(device_id, cmd)  # mqtt
        # сделать проверку что ф-ция сработала как в RF24
        #if (send_esp32(cmd)): print("ОК")

    
    return render_template('index.html', devices=devices, lives=lives, scenaries=scenaries)

@app.route("/api/status", methods=["GET"])
def get_status():
    data = {"devices": devices, "lives": lives}

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2
        )


@app.route("/scenaries", methods=["POST"])
def handle_scen():
    if request.method == "POST":
        if_dev = request.form.get('if_dev')
        oper = request.form.get('oper')
        if_val = request.form.get('if_val')
        then_dev = request.form.get('then_dev')
        then_cmd = request.form.get('then_cmd')

        if (if_dev != then_dev):
            scen_id = len(scenaries)
            scenaries[scen_id] = {
                "if_dev": if_dev,
                "oper": oper,
                "if_val": if_val,
                "then_dev": then_dev,
                "then_cmd": then_cmd
                }
        else:
            print("ошибка: if_dev == then_dev")
            
        
    return render_template('index.html', devices=devices, lives=lives, scenaries=scenaries)


# Получаем запрос от Яндекса и возвращаем ответ
# req - запрос от яндекса
# подробнее в доке: https://yandex.ru/dev/dialogs/alice/doc/ru/response
# пример: https://github.com/yandex/alice-skills/blob/master/python/buy-elephant/now/api.py
# !!!! URL выдуманный (поменять на настоящий) !!!!
@app.route("/alice/6krzTZQ7OJmUb3xTHXs1J5sD4UIPgqh5Ry6TqtMoNo8", methods=["POST"])
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
    device_id = request.form.get('device_id')
    if (req['session']['new']): res['response']['text'] = 'Привет! Я умею только включать и выключать свет'  # !! баг
    if ("включи" in req["request"]["command"] and
        "свет" in req["request"]["command"]
        ):
        res['response']['text'] = 'Включаю свет'
        toDevice(device_id, "ON")

    elif ("выключи" in req["request"]["command"] and
        "свет" in req["request"]["command"]
        ):
        res['response']['text'] = 'Выключаю'
        toDevice(device_id, "OFF")

    else:
        res['response']['text'] = 'Не поняла. Я умею только включать и выключать свет'

    # ответ яндексу
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

    print("devices: \n", devices)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
