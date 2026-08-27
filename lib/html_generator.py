#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from database import SiteDatabase

class HTMLGenerator:
    def __init__(self, db_path='sites.db', template_path='../template/index.html', output_path='index.html'):
        self.db = SiteDatabase(db_path)
        self.template_path = template_path
        self.output_path = output_path
    
    def generate_site_row(self, site, url_type="clearnet"):
        main_url = ''
        for url in site['urls']:
            if url['type'] == 'clearnet':
                main_url = url['url']
                break
        if not main_url and site['urls']:
            main_url = site['urls'][0]['url']
        
        button_html = f'''<td class="name">
  <a href="{main_url}" target="_blank">
   <img src="img/b/{site['button']}" alt="{site['name']}">
  </a>
</td>'''
        about_html = f'''<td>
{site['about']}<br>
<small>Доступен по: {', '.join([f'<a href="{u["url"]}" target="_blank">{u["type"]}</a>' for u in site['urls']])}</small>
</td>'''
        return f'<tr>\n{button_html}\n{about_html}\n</tr>'
    def get_table_rows(self):
        grouped_sites = self.db.get_sites_by_type()
        table_content = []
        for site_type, sites in grouped_sites.items():
          table_content.append(f'<tr><th colspan="2">{site_type.upper()}</th></tr>')
          
          for site in sites:
              table_content.append(self.generate_site_row(site))
        return '\n'.join(table_content)
    
    def generate_html(self):
        final_html = self.generate_list()
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"HTML страница успешно сгенерирована: {self.output_path}")
    def generate_list(self):
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        else:
            print(os.listdir('.'))
            print(self.template_path)
            return \
'''
<pre>
    /\\
 _ /  \\
/ \\| X|  _
|x||[]| //
Ничего не нашлось
</pre>
'''
        return template.replace('<!--TABLE-->', self.get_table_rows())
