from flask import Flask, render_template, request
import time

app = Flask(__name__)

## !! от старого датчика
def send_cmd(cmd):
    if cmd == "1":
        data = b"\x01"
    elif cmd == "0":
        data = b"\x00"

    time.sleep(1)    ## !!! ТАЙМЕР
    return report


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        cmd = request.form.get('submit')   # обращаемся к полю submit (name="submit")
        #print(cmd)  # отладка
        
        # проверка что команда корректная
        # ...
        
        res = send_cmd(cmd)
        if res:
            print("ОК")
    
    return render_template('index.html')


if __name__ == '__main__':
    # отправляем команду на esp32
