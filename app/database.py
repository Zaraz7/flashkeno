import sqlite3

class SiteDatabase:
    def __init__(self, db_path='sites.db'):
        self.db_path = db_path
        self.init_database()

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
            self._init_default_data(c)
            conn.commit()

    def _init_default_data(self, cursor):
        site_types = ['персональные сайты', 'соцсети', 'форумы']
        for t in site_types:
            cursor.execute('INSERT OR IGNORE INTO site_type (name) VALUES (?)', (t,))
        url_types = ['clearnet', 'yggdrasil', 'i2p', 'zeronet', 'gemini']
        for t in url_types:
            cursor.execute('INSERT OR IGNORE INTO url_type (name) VALUES (?)', (t,))

    # --- helper ---
    # def ensure_position_column(self):
    #     with self.get_connection() as conn:
    #         c = conn.cursor()
    #         c.execute("PRAGMA table_info(site)")
    #         cols = [r[1] for r in c.fetchall()]
    #         if 'position' not in cols:
    #             c.execute('ALTER TABLE site ADD COLUMN position INTEGER')
    #             c.execute('SELECT id FROM site ORDER BY id')
    #             for idx, (sid,) in enumerate(c.fetchall(), start=1):
    #                 c.execute('UPDATE site SET position = ? WHERE id = ?', (idx, sid))
    #             conn.commit()

    # --- CRUD and queries ---
    def add_site(self, name, button, about, type_name, urls):
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
            if row[6]:
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

    def delete_site(self, site_id):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM site WHERE id = ?', (site_id,))
            conn.commit()
            return c.rowcount > 0

    def move_site(self, site_id, direction):
        """
        Перемещает сайт вверх/вниз относительно порядка по id, реализовано как swap содержимого
        с соседней записью (меняются поля site и связанные url'ы остаются у тех же id'ов).
        Возвращает True при успехе, False если нельзя переместить.
        """
        with self.get_connection() as conn:
            c = conn.cursor()
            # Получаем все id в порядке возрастания
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
                # Начинаем транзакцию
                # Считываем поля site для обеих записей
                c.execute('SELECT name, button, about, type_id FROM site WHERE id = ?', (site_id,))
                row1 = c.fetchone()
                c.execute('SELECT name, button, about, type_id FROM site WHERE id = ?', (other_id,))
                row2 = c.fetchone()
                if not row1 or not row2:
                    return False

                # Обмен полями site
                c.execute('UPDATE site SET name = ?, button = ?, about = ?, type_id = ? WHERE id = ?',
                        (row2[0], row2[1], row2[2], row2[3], site_id))
                c.execute('UPDATE site SET name = ?, button = ?, about = ?, type_id = ? WHERE id = ?',
                        (row1[0], row1[1], row1[2], row1[3], other_id))

                # Теперь нужно обменять url'ы так, чтобы внешние ссылки на site_id остались корректны.
                # Подход: временно пометить site_id -> -1, other_id -> site_id, -1 -> other_id
                # Используем временную negative marker в отдельной временной таблице mapping.
                # Проще: переместим url строки, меняя site_id у url записей.
                # Чтобы избежать конфликтов, используем temp id = -site_id
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