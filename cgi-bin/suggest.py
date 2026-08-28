#!/usr/bin/env python3

import cgi
import sys
import codecs
import os

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
form = cgi.FieldStorage()

COLS = ('email', 'name', 'url', 'button', 'about', 'type_id')
REQUARED = ('name', 'url', 'about', 'type')

client_ip = os.environ.get("REMOTE_ADDR", "None")
client_agent = os.environ.get('HTTP_USER_AGENT', 'Чудоюдо')

with open('db/suggests.csv', 'a', encoding='utf-8') as f:
    f.write(f'"{client_ip}"; "date"; "{client_agent}"')
    for key in COLS:
        f.write(f';\t"{form.getfirst(key, "None")}"')
    f.write('\n')

print("Content-type: text/html\n")
print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Обработка данных форм</title>
        </head>
        <body>""")
print("<h1>-</h1>")
print("""</body>
        </html>""")