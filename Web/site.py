from flask import Flask, render_template, request
import time, requests

ESP_IP= "http://192.168.0.16";
app = Flask(__name__)

def send_cmd(cmd):
    # проверка что команда корректная
    # ...
    url = f"{ESP_IP}/?command={cmd}"
    print(url)

    ## не всегда доходят
    try:
        requests.get(url, timeout=2)
    except:
        print("ошибка")



@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        cmd = request.form.get('submit')   # обращаемся к полю submit (name="submit")
        send_cmd(cmd)
        #print(request.form.get('submit'))  # отладка
        #if (send_cmd(cmd)): print("ОК")
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
