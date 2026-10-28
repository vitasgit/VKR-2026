ssh-ключ и проброс портов
1) ssh-keygen -t ed25519
+ сделал парольную фразу
2) ssh-copy-id vibfeynman@185.88.101.162
3) ssh -N -R 127.0.0.1:6000:localhost:5000 vps2 
    - (vps2 - алиас в ~/.ssh/config)
    - VPS слушает 6000 порт и пробрасывает домой на 5000

--- Заметка про GatewayPorts
проверяем что проброс портов закрыты /etc/ssh/sshd_config
подключаться может только конектерный ip
GatewayPorts no

• Если GatewayPorts no (по умолчанию): SSH-сервер привязывает порт 8080 строго к адресу 127.0.0.1 (localhost). Это значит, что зайти на ваш домашний сайт сможет только сам облачный сервер (изнутри своей консоли). Любой внешний пользователь из интернета, введя http://IP_сервера:8080, получит ошибку доступа.
• Если GatewayPorts yes: SSH-сервер привязывает проброшенный порт к адресу 0.0.0.0 (ко всем сетевым интерфейсам). Теперь любой человек из интернета или локальной сети может ввести http://IP_сервера:8080 и попадет прямо на ваш домашний компьютер.
---

4) Привязка домена DuckDNS к VPS
- Зарегистрирован бесплатный поддомен `umnyjdom.duckdns.org`.
- A-запись: в поле `current ip` указать IP-адрес VPS.
- Проверка DNS-привязки:
  ```bash
  nslookup umnyjdom.duckdns.org
  ```

5) Установка Nginx, Certbot на VPS для проксирования и сертификата tls
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx apache2-utils
```
Открытие веб-портов 80 и 443 в файрволе (чтобы получить сертификат от letsencrypt нужно открыть порт 80, 443 для https):
```bash
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp
sudo ufw status verbose
```

6) Выпуск TLS-сертификата letsencrypt через Certbot (на VPS)
```bash
sudo certbot --nginx -d umnyjdom.duckdns.org
```
certbot сам выпускает сертификат, кладет в корень системы, отправляет запрос на провреку, формирует конфиг nginx
сертификаты: `/etc/letsencrypt/live/umnyjdom.duckdns.org/`;
конфиг nginx: `/etc/nginx/sites-available/default`;

7) авторизация через htpasswd
```bash
sudo htpasswd -c /etc/nginx/.htpasswd vitaly
```
- Флаг `-c` создаёт новый файл (используется только для первого пользователя).
- В файле хранятся логин и хеш пароля.

8) Настройка Nginx server-блока  (/etc/nginx/sites-available/default)
```
location / {
        auth_basic "awfaf";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:6000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
}
```
Проверка синтаксиса и перезагрузка nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

Проверка портов:
```bash
sudo ss -tlpn
```
