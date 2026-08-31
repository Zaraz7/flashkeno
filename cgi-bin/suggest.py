#!/usr/bin/env python3

import cgi
import sys
import codecs
import os
from pathlib import Path

# Добавляем путь к lib
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.database import SiteDatabase

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
form = cgi.FieldStorage()

client_ip = os.environ.get("REMOTE_ADDR", "None")
client_agent = os.environ.get('HTTP_USER_AGENT', 'Чудоюдо')

# Получаем данные из формы
email = form.getfirst("email", "")
name = form.getfirst("name", "")
url = form.getfirst("url", "")
button = form.getfirst("button", "")
about = form.getfirst("about", "")
type_id = form.getfirst("type_id", "")

# Проверка обязательных полей
if not all([name, url, about, type_id]):
    print("Content-type: text/html\n")
    print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Ошибка</title>
        </head>
        <body>
            <h1>Ошибка: Заполните все обязательные поля</h1>
            <p><a href="/suggest.html">Вернуться</a></p>
        </body>
        </html>""")
    sys.exit()

try:
    # Инициализируем БД
    db = SiteDatabase(Path(__file__).parent.parent / 'db' / 'sites.db')
    
    # Добавляем заявку в БД
    suggestion_id = db.add_suggestion(
        email=email,
        name=name,
        url=url,
        button=button,
        about=about,
        type_id=type_id,
        client_ip=client_ip,
        client_agent=client_agent
    )
    
    print("Content-type: text/html\n")
    print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Заявка отправлена</title>
        </head>
        <body>
            <h1>Спасибо за заявку!</h1>
            <p>Ваша заявка принята и будет рассмотрена в ближайшее время.<br>
            Номер заявки: {}<br>
            <a href="/">Вернуться на главную</a></p>
        </body>
        </html>""".format(suggestion_id))
    
except Exception as e:
    print("Content-type: text/html\n")
    print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Ошибка</title>
        </head>
        <body>
            <h1>Ой ей</h1>
            <p>Попробуйте позже или свяжитесь с администратором. Эта штука не должна была так себя повести.<br>
            Ошибка: {}</p>
        </body>
        </html>""".format(str(e)))