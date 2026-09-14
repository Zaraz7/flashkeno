import sqlite3


def parse_urls_from_text(urls_text):
    from ipaddress import ip_address, AddressValueError
    """
    Преобразует текст с URLs (разделённых переносами строк) в список кортежей (тип, url).
    
    Типы определяются по следующим правилам:
    - https:// → https
    - http://*.i2p → i2p
    - http://[IPv6] → yggdrasil
    - http://*.{ygg,anon,btn,conf,index,merch,mirror,mob,screen,srv} → yggdrasil-alfis
    - http://127.0.0.1:43110 → zeronet
    - http:// (остальное) → http
    - gemini:// → gemini
    
    Args:
        urls_text: строка с URLs, разделённые переносами строк
    
    Returns:
        список кортежей (тип, url)
    """
    if not urls_text:
        return []
    
    urls = []
    lines = urls_text.strip().split('\n')
    yggdrasil_alfis_domains = {'.ygg', '.anon', '.btn', '.conf', '.index', '.merch', '.mirror', '.mob', '.screen', '.srv'}
    
    for line in lines:
        url = line.strip()
        if not url:
            continue
        
        url_type = None
        
        # gemini://
        if url.startswith('gemini://'):
            url_type = 'gemini'
        
        # https://
        elif url.startswith('https://'):
            url_type = 'https'
        
        # http://
        elif url.startswith('http://'):
            # Извлекаем хост из URL
            host_part = url[7:]  # Убираем 'http://'
            
            # Извлекаем хост (до первого / или :)
            host = host_part.split('/')[0].split(':')[0]
            
            # Проверяем IPv6 (заключён в квадратные скобки или содержит :)
            if host.startswith('[') or ':' in host:
                try:
                    # Если это валидный IPv6
                    ip_address(host.strip('[]'))
                    url_type = 'yggdrasil'
                except (AddressValueError, ValueError):
                    pass
            
            # Проверяем .i2p
            if not url_type and host.lower().endswith('.i2p'):
                url_type = 'i2p'
            
            # Проверяем zeronet
            if not url_type and url.startswith('http://127.0.0.1:43110'):
                url_type = 'zeronet'
            
            # Проверяем yggdrasil-alfis по доменам
            if not url_type:
                for domain in yggdrasil_alfis_domains:
                    if host.lower().endswith(domain):
                        url_type = 'yggdrasil-alfis'
                        break
            
            # По умолчанию http
            if not url_type:
                url_type = 'http'
        
        if url_type:
            urls.append((url_type, url))
    
    return urls
class SiteDatabase:
    def __init__(self, db_path='sites.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS site_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS site (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    button TEXT NOT NULL,
                    about TEXT,
                    type_id INTEGER,
                    FOREIGN KEY (type_id) REFERENCES site_type(id)
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS url_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS url (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    type_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
                    FOREIGN KEY (type_id) REFERENCES url_type(id)
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS suggestion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    button TEXT,
                    about TEXT,
                    type_id INTEGER,
                    client_ip TEXT,
                    client_agent TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (type_id) REFERENCES site_type(id)
                )
            ''')
            self._init_default_data(c)
            conn.commit()

    def _init_default_data(self, cursor):
        site_types = ['персональные сайты', 'соцсети', 'форумы', 'другое']
        for t in site_types:
            cursor.execute('INSERT OR IGNORE INTO site_type (name) VALUES (?)', (t,))
        # TODO: ? Switch from "clearnet" to http, https
        url_types = ['clearnet', 'yggdrasil', 'yggdrasil-alfis', 'i2p', 'zeronet', 'gemini', 'http', 'https']
        for t in url_types:
            cursor.execute('INSERT OR IGNORE INTO url_type (name) VALUES (?)', (t,))

    def migrate_add_main_url(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute('''
                    ALTER TABLE site ADD COLUMN main_url INTEGER 
                    REFERENCES url(id) ON DELETE SET NULL
                ''')
                conn.commit()
                print("Migration: main_url column added successfully")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("Migration: main_url column already exists")
                else:
                    raise
    def add_site(self, name, button, about, type_name, urls, main_url_id=None):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM site_type WHERE name = ?', (type_name,))
            r = c.fetchone()
            if r:
                type_id = r[0]
            else:
                c.execute('INSERT INTO site_type (name) VALUES (?)', (type_name,))
                type_id = c.lastrowid
            # compute next position
            c.execute('SELECT MAX(id) FROM site')
            maxpos = c.fetchone()[0] or 0
            pos = maxpos + 1
            c.execute('INSERT INTO site (name, button, about, type_id) VALUES (?, ?, ?, ?)',
                      (name, button, about, type_id))
            site_id = c.lastrowid
            for url_type_name, url in urls or []:
                c.execute('SELECT id FROM url_type WHERE name = ?', (url_type_name,))
                r = c.fetchone()
                if r:
                    url_type_id = r[0]
                else:
                    c.execute('INSERT INTO url_type (name) VALUES (?)', (url_type_name,))
                    url_type_id = c.lastrowid
                c.execute('INSERT INTO url (site_id, type_id, url) VALUES (?, ?, ?)', (site_id, url_type_id, url))
            conn.commit()
            return site_id

    def get_all_sites(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT s.id, s.name, s.button, s.about, st.name as site_type,
                       GROUP_CONCAT(ut.name || ':' || u.url, '|') as urls
                FROM site s
                LEFT JOIN site_type st ON s.type_id = st.id
                LEFT JOIN url u ON s.id = u.site_id
                LEFT JOIN url_type ut ON u.type_id = ut.id
                GROUP BY s.id
                ORDER BY st.id, s.id
            ''')
            sites = []
            for row in c.fetchall():
                site = {'id': row[0], 'name': row[1], 'button': row[2], 'about': row[3],
                        'type': row[4], 'urls': []}
                if row[5]:
                    for url_item in row[5].split('|'):
                        typ, url = url_item.split(':', 1)
                        site['urls'].append({'type': typ, 'url': url})
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

    def get_site(self, site_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM site WHERE id = ?', (site_id,))
            if not c.fetchone():
                return None
            c.execute('''
                SELECT s.id, s.name, s.button, s.about, st.name as site_type,
                       GROUP_CONCAT(ut.name || ':' || u.url, '|') as urls
                FROM site s
                LEFT JOIN site_type st ON s.type_id = st.id
                LEFT JOIN url u ON s.id = u.site_id
                LEFT JOIN url_type ut ON u.type_id = ut.id
                WHERE s.id = ?
                GROUP BY s.id
            ''', (site_id,))
            row = c.fetchone()
            site = {'id': row[0], 'name': row[1], 'button': row[2], 'about': row[3],
                    'type': row[4], 'urls': []}
            if len(row) > 6 and row[6]:
                for url_item in row[6].split('|'):
                    typ, url = url_item.split(':', 1)
                    site['urls'].append({'type': typ, 'url': url})
            return site

    def update_site(self, site_id, name=None, button=None, about=None, type_name=None):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM site WHERE id = ?', (site_id,))
            if not c.fetchone():
                return False
            if name is not None:
                c.execute('UPDATE site SET name = ? WHERE id = ?', (name, site_id))
            if button is not None:
                c.execute('UPDATE site SET button = ? WHERE id = ?', (button, site_id))
            if about is not None:
                c.execute('UPDATE site SET about = ? WHERE id = ?', (about, site_id))
            if type_name is not None:
                c.execute('SELECT id FROM site_type WHERE name = ?', (type_name,))
                r = c.fetchone()
                if r:
                    type_id = r[0]
                else:
                    c.execute('INSERT INTO site_type (name) VALUES (?)', (type_name,))
                    type_id = c.lastrowid
                c.execute('UPDATE site SET type_id = ? WHERE id = ?', (type_id, site_id))
            conn.commit()
            return True

    def replace_urls(self, site_id, urls):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM site WHERE id = ?', (site_id,))
            if not c.fetchone():
                return False
            c.execute('DELETE FROM url WHERE site_id = ?', (site_id,))
            for url_type_name, url in urls or []:
                c.execute('SELECT id FROM url_type WHERE name = ?', (url_type_name,))
                r = c.fetchone()
                if r:
                    url_type_id = r[0]
                else:
                    c.execute('INSERT INTO url_type (name) VALUES (?)', (url_type_name,))
                    url_type_id = c.lastrowid
                c.execute('INSERT INTO url (site_id, type_id, url) VALUES (?, ?, ?)', (site_id, url_type_id, url))
            conn.commit()
            return True
    def set_main_url(self, site_id, main_url_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM site WHERE id = ?', (site_id,))
            if not c.fetchone():
                return False
            c.execute('SELECT id FROM url WHERE id = ?', (main_url_id,))
            if not c.fetchone():
                return False
            c.execute('UPDATE site SET main_url_id = ? WHERE id = ?', (main_url_id, site_id))
            conn.commit()
            return True


    def delete_site(self, site_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM site WHERE id = ?', (site_id,))
            conn.commit()
            return c.rowcount > 0

    def move_site(self, site_id, direction):
        # if successfully moved True, else False 
        with self.get_connection() as conn:
            c = conn.cursor()
            # TODO: Make method
            c.execute('SELECT id FROM site ORDER BY id')
            ordered = [r[0] for r in c.fetchall()]
            if site_id not in ordered:
                return False
            idx = ordered.index(site_id)
            if direction == 'up':
                if idx == 0:
                    return False
                other_id = ordered[idx - 1]
            elif direction == 'down':
                if idx == len(ordered) - 1:
                    return False
                other_id = ordered[idx + 1]
            else:
                return False

            try:
                # Transaction
                c.execute('SELECT name, button, about, type_id FROM site WHERE id = ?', (site_id,))
                row1 = c.fetchone()
                c.execute('SELECT name, button, about, type_id FROM site WHERE id = ?', (other_id,))
                row2 = c.fetchone()
                if not row1 or not row2:
                    return False

                c.execute('UPDATE site SET name = ?, button = ?, about = ?, type_id = ? WHERE id = ?',
                        (row2[0], row2[1], row2[2], row2[3], site_id))
                c.execute('UPDATE site SET name = ?, button = ?, about = ?, type_id = ? WHERE id = ?',
                        (row1[0], row1[1], row1[2], row1[3], other_id))

                # XXX: Maybe need to add `position` cell. Changing `id` on urls is mess...
                temp_id = -site_id
                c.execute('UPDATE url SET site_id = ? WHERE site_id = ?', (temp_id, site_id))
                c.execute('UPDATE url SET site_id = ? WHERE site_id = ?', (site_id, other_id))
                c.execute('UPDATE url SET site_id = ? WHERE site_id = ?', (other_id, temp_id))

                conn.commit()
                return True
            except Exception:
                conn.rollback()
                raise


    def find_sites(self, query):
        with self.get_connection() as conn:
            c = conn.cursor()
            q = f'%{query}%'
            c.execute('''
                SELECT s.id, s.name, s.button, s.about, st.name as site_type
                FROM site s
                LEFT JOIN site_type st ON s.type_id = st.id
                WHERE s.name LIKE ? OR s.about LIKE ?
                ORDER BY s.id
            ''', (q, q))
            return [{'id': r[0], 'name': r[1], 'button': r[2], 'about': r[3], 'type': r[4], 'position': r[5]} for r in c.fetchall()]

    def add_suggestion(self, email, name, url, button, about, type_id, client_ip, client_agent):
        with self.get_connection() as conn:
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO suggestion (email, name, url, button, about, type_id, client_ip, client_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, name, url, button, about, type_id, client_ip, client_agent))
            conn.commit()
            return c.lastrowid

    def get_suggestions(self, status=None):
        with self.get_connection() as conn:
            c = conn.cursor()
            query = '''
                SELECT s.id, s.email, s.name, s.url, s.button, s.about, 
                       st.name as site_type, s.client_ip, s.client_agent, 
                       s.submitted_at, s.status
                FROM suggestion s
                LEFT JOIN site_type st ON s.type_id = st.id
            '''
            params = []
            if status:
                query += ' WHERE s.status = ?'
                params.append(status)
            query += ' ORDER BY s.submitted_at DESC'
            
            c.execute(query, params)
            suggestions = []
            for row in c.fetchall():
                suggestions.append({
                    'id': row[0],
                    'email': row[1],
                    'name': row[2],
                    'url': row[3],
                    'button': row[4],
                    'about': row[5],
                    'type': row[6],
                    'client_ip': row[7],
                    'client_agent': row[8],
                    'submitted_at': row[9],
                    'status': row[10]
                })
            return suggestions

    def update_suggestion_status(self, suggestion_id, status):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('UPDATE suggestion SET status = ? WHERE id = ?', (status, suggestion_id))
            conn.commit()
            return c.rowcount > 0

    def delete_suggestion(self, suggestion_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM suggestion WHERE id = ?', (suggestion_id,))
            conn.commit()
            return c.rowcount > 0

    def get_suggestion(self, suggestion_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT s.id, s.email, s.name, s.url, s.button, s.about, 
                       st.name as site_type, s.client_ip, s.client_agent, 
                       s.submitted_at, s.status
                FROM suggestion s
                LEFT JOIN site_type st ON s.type_id = st.id
                WHERE s.id = ?
            ''', (suggestion_id,))
            row = c.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'url': row[3],
                'button': row[4],
                'about': row[5],
                'type': row[6],
                'client_ip': row[7],
                'client_agent': row[8],
                'submitted_at': row[9],
                'status': row[10]
            }

    def approve_suggestion(self, suggestion_id):
        suggestion = self.get_suggestion(suggestion_id)
        if not suggestion or suggestion['status'] != 'pending':
            return False
        
        # Преобразуем URLs из текста в список кортежей
        urls = parse_urls_from_text(suggestion['url'])
        
        if not urls:
            return False
        
        site_id = self.add_site(
            name=suggestion['name'],
            button=suggestion['button'] or '',
            about=suggestion['about'],
            type_name=suggestion['type'] or 'другое',
            urls=urls
        )
        
        if site_id:
            # Устанавливаем первый URL как главный
            first_url_id = self._get_first_url_id(site_id)
            if first_url_id:
                self.set_main_url(site_id, first_url_id)
            
            self.update_suggestion_status(suggestion_id, 'approved')
            return site_id
        return False
    def _get_first_url_id(self, site_id):
        """Получает ID первого URL для сайта (в порядке добавления)"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT id FROM url 
                WHERE site_id = ? 
                ORDER BY id ASC 
                LIMIT 1
            ''', (site_id,))
            row = c.fetchone()
            return row[0] if row else None