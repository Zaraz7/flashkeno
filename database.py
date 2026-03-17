import sqlite3
import os

class SiteDatabase:
    def __init__(self, db_path='sites.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица типов сайтов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS site_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS site (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    button TEXT NOT NULL,
                    about TEXT,
                    type_id INTEGER,
                    FOREIGN KEY (type_id) REFERENCES site_type(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    type_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
                    FOREIGN KEY (type_id) REFERENCES url_type(id)
                )
            ''')
            
            self._init_default_data(cursor)
            
            conn.commit()
    
    def _init_default_data(self, cursor):
        site_types = ['персональные сайты', 'соцсети', 'форумы']
        for type_name in site_types:
            cursor.execute('INSERT OR IGNORE INTO site_type (name) VALUES (?)', (type_name,))
        
        url_types = ['clearnet', 'yggdrasil', 'i2p', 'zeronet', 'gemini']
        for type_name in url_types:
            cursor.execute('INSERT OR IGNORE INTO url_type (name) VALUES (?)', (type_name,))
    
    def add_site(self, name, button, about, type_name, urls):
        """
        Добавляет новый сайт с URL-ами
        
        Args:
            name: название сайта
            button: имя файла кнопки (например, 'button1.gif')
            about: описание сайта
            type_name: название типа сайта
            urls: список кортежей (url_type_name, url)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM site_type WHERE name = ?', (type_name,))
            type_row = cursor.fetchone()
            if type_row:
                type_id = type_row[0]
            else:
                cursor.execute('INSERT INTO site_type (name) VALUES (?)', (type_name,))
                type_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO site (name, button, about, type_id)
                VALUES (?, ?, ?, ?)
            ''', (name, button, about, type_id))
            
            site_id = cursor.lastrowid
            
            for url_type_name, url in urls:
                cursor.execute('SELECT id FROM url_type WHERE name = ?', (url_type_name,))
                url_type_row = cursor.fetchone()
                if url_type_row:
                    url_type_id = url_type_row[0]
                else:
                    cursor.execute('INSERT INTO url_type (name) VALUES (?)', (url_type_name,))
                    url_type_id = cursor.lastrowid
                
                cursor.execute('''
                    INSERT INTO url (site_id, type_id, url)
                    VALUES (?, ?, ?)
                ''', (site_id, url_type_id, url))
            
            conn.commit()
            return site_id
    
    def get_all_sites(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    s.id,
                    s.name,
                    s.button,
                    s.about,
                    st.name as site_type,
                    GROUP_CONCAT(ut.name || ':' || u.url, '|') as urls
                FROM site s
                LEFT JOIN site_type st ON s.type_id = st.id
                LEFT JOIN url u ON s.id = u.site_id
                LEFT JOIN url_type ut ON u.type_id = ut.id
                GROUP BY s.id
                ORDER BY st.name, s.name
            ''')
            
            sites = []
            for row in cursor.fetchall():
                site = {
                    'id': row[0],
                    'name': row[1],
                    'button': row[2],
                    'about': row[3],
                    'type': row[4],
                    'urls': []
                }
                
                if row[5]:
                    for url_item in row[5].split('|'):
                        url_type, url = url_item.split(':', 1)
                        site['urls'].append({'type': url_type, 'url': url})
                
                sites.append(site)
            
            return sites
    
    def get_sites_by_type(self):
        sites = self.get_all_sites()
        grouped = {}
        
        for site in sites:
            site_type = site['type']
            if site_type not in grouped:
                grouped[site_type] = []
            grouped[site_type].append(site)
        
        return grouped