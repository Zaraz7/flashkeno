#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from database import SiteDatabase

class HTMLGenerator:
    def __init__(self, db_path='sites.db', template_path='template.html', output_path='index.html'):
        self.db = SiteDatabase(db_path)
        self.template_path = template_path
        self.output_path = output_path
    
    def generate_site_row(self, site):
        main_url = ''
        for url in site['urls']:
            if url['type'] == 'clearnet':
                main_url = url['url']
                break
        if not main_url and site['urls']:
            main_url = site['urls'][0]['url']
        
        button_html = f'''<td>
  <a href="{main_url}" target="_blank">
   <img src="img/b/{site['button']}" alt=" "><br>
   {site['name']}
  </a>
</td>'''
        
        about_html = f'''<td>
{site['about']}<br>
<small>Также доступен в: {', '.join([f'<a href="{u["url"]}" target="_blank">{u["type"]}</a>' for u in site['urls']])}</small>
</td>'''
        
        return f'<tr>\n{button_html}\n{about_html}\n</tr>'
    
    def generate_html(self):
        grouped_sites = self.db.get_sites_by_type()
        
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            template = self._create_default_template()
        
        table_content = []
        
        for site_type, sites in grouped_sites.items():
            table_content.append(f'<tr><th colspan="2">{site_type.upper()}</th></tr>')
            
            for site in sites:
                table_content.append(self.generate_site_row(site))
        
        final_html = template.replace('<!-- TABLE_CONTENT -->', '\n'.join(table_content))
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"HTML страница успешно сгенерирована: {self.output_path}")
    
    def _create_default_template(self):
        return '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {width:80ch; margin:auto;background-color:#FFF;color:#222;font-family:'Courier New',Courier,monospace;}
p, pre, code {margin:0;font-family:'Courier New',Courier,monospace;font-size:16px;}
pre {line-height:1}
th {background-color:#888;color:#FFF}
.ascii {font-size:80%;line-height:0.9}
.disabled {pointer-events: none;color: #888888;}

@media (max-width:770px) {
body {width:auto;}
p{margin-left: 5px;}
.fr, .fc {display:none;}
.art-table td, .art-table th {width:auto;}}
@media (prefers-color-scheme: dark){
body {background-color:#222;color:#FFF;}
a {color:#0AF;}
th {color:#222}}
</style>
</head>
<center>
<pre class="ascii">

 ___   ### _________________________________________ 
|    ####/                                          |
|   ##'    ,#  /##, #  #  #  #  // #   #  #  # .##, |
|   ##    #"# /#..# #  #  # ,#,// .#  ## ,#  # #  # |
| /#####/ # # #""' // // // #""|| #  ##' #""#' #  # |
|   ##   #' # "##' #######  #   # ##" #  #  #  "##' |
   ##' _____________________________________________|
/###'                                               
##'    ${Каталог русскоговорящих || СНГ инди сайтов}

</pre>
</center>
<p>Это попытка собрать в единую кучу персональный, самодельный, переферийный Рунет. Этот сайт не о социальных сетях мегаполисах или о крупных группах, что находятся у магистрали известных мессенжеров. Это про маленькие городки федиверса, форумы-деревни и хуторы домашние страницы.</p>
<p>Идея <a href="https://baseddogblog.neocities.org/rusindieweb/">не нова</a>, но хотелось бы видеть список длиннее и актуальнее. Чтож, почему бы не сделать его своими усилиями?</p>
<center>
<pre>

<span style="background-color:yellow;color:black;">/// under construction ///</span>

</pre>
</center>
<p>Пока список состоит из домашних страниц, но в будущем планируем дополнить)</p>
<br>
<hr>
<table border="0" cellpadding="0" cellspacing="9">
  <tr>
    <th>Сайт</th>
    <th>Описание</th>
  </tr>
<!-- TABLE_CONTENT -->
</table>
<hr>
<p>У вас есть что предложить? Или же ваш <i>знакомый</i> имеет свой сайтец? Пришлите <b>ссылку, название и описание</b> ресурса. Адрес почтового ящика вы можете получить, нажав на кнопку ниже:</p>
<center>
  <input id="btnEmail" type="button" value="Получить адрес!" />
<a id="aEmail" href="#" class="disabled">
<pre id="cipher">zftI%izRAp0;^;,
baonyk!4@o_g1#K
!RrJ|%25^etw\zN
0#ra^sB|.p*jmP*
VPF,zh4lfNyc+YT
t.WHN7y+%(fi#n)
inLx|A@%M$I43Uu
il__ENYw|wXN+]T
PBeDCDsB1AyIz4Z
1^aWlz>[[08p[^b
cMNJPLwA\l.wiT"
gh{(hf_@)_.sh!m
Zo3.w}WN>JOli$D
/hX|tselzEEc*t7
evUXbm$AK_,Ot_e</pre></a>
<script type="text/javascript">
    const btnEmail = document.getElementById('btnEmail');
    const cipher = document.getElementById('cipher');
    btnEmail.addEventListener('click', emailEvent);
    function emailEvent() {
        btnEmail.disabled = true;
        btnEmail.value = 'Расшифровка...';
        const lenght = 16; 
        var index = 1;
        var start = '';
        const id = setInterval(() => {
            if (cipher.textContent.length <= lenght + 5) { 
                clearInterval(id); 
                btnEmail.value = 'Готово!';
                const a = document.getElementById('aEmail');
                a.href = 'mailto:'+cipher.textContent;
                a.classList.remove('disabled');
                return; 
            }
            const start = cipher.textContent.slice(0,index) || '';
            cipher.textContent = start + cipher.textContent.slice(index+lenght);
            index++;
        }, 170);
    }
</script>
</center>
<p>Или вы можете прочитать адресс по главной диагонали в матрице из символов выше.</p>
<hr>
<p class="footer">Администрируется <a href="http://zaraz7.narod.ws" target="_blank">Zaraz7</a>.</p>
</body>
</html>'''