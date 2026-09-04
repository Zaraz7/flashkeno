#!/usr/bin/env python3

import cgi
import sys
import codecs
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.database import SiteDatabase

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
form = cgi.FieldStorage()

client_ip = os.environ.get("REMOTE_ADDR", "None")
client_agent = os.environ.get('HTTP_USER_AGENT', 'Чудоюдо')

email = form.getfirst("email", "")
name = form.getfirst("name", "")
url = form.getfirst("url", "")
button = form.getfirst("button", "")
about = form.getfirst("about", "")
type_id = form.getfirst("type_id", "0")

head_jaw="""</title>
<style>
body {width:80ch; margin:auto;background-color:#FFF;color:#222;font-family:'Courier New',Courier,monospace;}
p, pre, code {margin:0;font-family:'Courier New',Courier,monospace;font-size:16px;}
pre {line-height:1}
th {background-color:#888;color:#FFF}
.ascii{font-size:70%;line-height:0.9;}
.disabled{pointer-events:none;color: #888888;}
a #cipher {text-decoration: none;height:28ch;}
.footer{font-style:italic;margin-bottom: 2ch;}
img{width:88px;height:31px;image-rendering:pixelated;}
.name{vertical-align:top;text-align:center;}

@media (max-width:770px) {
body {width:auto;}
p{margin-left: 5px;}
.fr, .fc {display:none;}
.art-table td, .art-table th {width:auto;}}
@media (prefers-color-scheme: dark){
body {background-color:#222;color:#FFF;}
a {color:#4AF;}
</style>
        </head>
        <body>
</center>"""
html_end="</center></body></html>"


print("Content-type: text/html\n")
print("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>""", end='')


if not all([name, url, about]):
    print('Чего чего?',head_jaw,"""<h1>Ошибка: Заполните все обязательные поля в заявке</h1>
<p><a href="/suggest.html">Вернуться</a></p>""", html_end)
    sys.exit()

try:
    db = SiteDatabase(Path(__file__).parent.parent / 'db' / 'sites.db')
    
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
    print('Заявка отправлена',head_jaw,"""
          <h1>Спасибо за заявку!</h1>
            <p>Ваша заявка принята и будет рассмотрена в ближайшее время.<br>
            Номер заявки: """,suggestion_id)

except Exception as e:
    print('Заявка отправлена',html_end,"""
          <h1>Ой ей</h1>
            <p>Попробуйте позже или свяжитесь с администратором. Эта штука не должна была так себя повести.<br>
            Ошибка: """,str(e))

print(html_end, '<br><a href="/">Вернуться на главную</a></p>')