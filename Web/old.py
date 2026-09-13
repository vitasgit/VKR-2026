from flask import Flask, render_template, request
from RF24 import RF24, RF24_PA_LOW, RF24_250KBPS#, RF24_DRIVER
import time


app = Flask(__name__)

def send_cmd(cmd):
    if cmd == "1":
        data = b"\x01"
    elif cmd == "0":
        data = b"\x00"
    
    report = radio.write(data)
    
    # if report:
    #     print(data, "OK")
    # else:
    #     print("Ошибка")

    time.sleep(1)
    return report


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        cmd = request.form.get('submit')  # обращаемся к полю submit (name="submit")
        cmd = request.form['submit']  # обращаемся к полю как к ключу словаря
        #print(cmd)  # отладка
        res = send_cmd(cmd)
        if res:
            print("ОК")
    
    return render_template('index.html')


if __name__ == '__main__':
    CE_PIN = 73  # pin 7 на плате
    CSN_PIN = 11  # для spidev1.1
    pipe1_addr = b"1Node"
    radio = RF24(CE_PIN, CSN_PIN)

    if not radio.begin():
        print("радиомодуль не подключен")
        #exit()
        
    radio.setPALevel(RF24_PA_LOW)        # мощность передатчика (low = -12 dBm)
    radio.setDataRate(RF24_250KBPS)      # Скорость передачи данных, чем меньше - тем дальше (скорость приема и передачи должна быть одинаковая)
    radio.setAutoAck(1);                 # режим подтверждения приёма, 1 вкл 0 выкл
    radio.setRetries(0, 15);             # (время между попыткой достучаться, число попыток) 15 - максимальное
    radio.setPayloadSize(1);             # пакет данных размером 1 байт (бубу передавать 1 или 0)
    radio.setChannel(76)                 # выбираем канал передачи данных с самыми низкими помехами
    radio.powerUp();                     # режим передачи (повышенного потребления), powerDown - режим ожидания
    radio.openWritingPipe(pipe1_addr);   # открыть канал на отправку
    radio.stopListening()                # режим передачи

    app.run(host='0.0.0.0', port=5000, debug=False)
