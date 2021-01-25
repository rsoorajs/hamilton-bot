from sqlite3 import connect as sqlite_conn


class sqlite:
    def __init__(self, file):
        self.file = file
        self.db = self.connect()

    def connect(self):
        self.connection = sqlite_conn(self.file)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def save(self):
        self.connection.commit()
        self.close()
        self.connect()

    def execute(self, cmd):
        self.cursor.execute(cmd)
        try:
            r = self.cursor.fetchall()
        except Exception:
            r = []
        return r


class crub:
    def __init__(self, sql, database=None,  **kwargs):
        self.conn = sql(**kwargs)
        if database:
            self.conn.execute(f"USE {database};")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS flood(
                id INTEGER,
                amount INTEGER
            );"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS welcome(
                id INTEGER,
                hello TEXT
            );"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS filters(
                id INTEGER,
                word TEXT,
                caption TEXT,
                file_id TEXT,
                file_type TEXT
            );"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS language(
                id INTEGER,
                code TEXT
            );"""
        )
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS rules(
                id INTEGER,
                rule TEXT
            );"""
        )
        self.conn.save()

    # Welcome
    def get_welcome(self, cid):
        r = self.conn.execute(
            f"SELECT (hello) FROM welcome WHERE id = '{cid}';"
        )[0][0]
        return r

    def set_welcome(self, cid, text):
        try:
            r = self.get_welcome(cid)
        except Exception:
            r = None
        if r:
            self.conn.execute(
                f"UPDATE welcome SET hello = '{text}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(
                f"INSERT INTO welcome VALUES ('{cid}', '{text}');"
            )
        self.conn.save()

    # Flood
    def get_flood(self, cid):
        r = self.conn.execute(
            f"SELECT (amount) FROM flood WHERE id = '{cid}';"
        )
        return r

    def set_flood(self, cid, limit):
        r = self.get_flood(cid)
        if r:
            self.conn.execute(
                f"UPDATE flood SET amount = '{limit}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(
                f"INSERT INTO flood VALUES ('{cid}', '{limit}');"
            )
        self.conn.save()

    # Filter
    def get_filter(self, cid, key):
        r = self.conn.execute(
            f"""SELECT caption, file_id, file_type FROM filters
            WHERE
                id = '{cid}' AND
                word = '{key}';"""
        )
        return r

    def get_filters(self, cid):
        r = self.conn.execute(f"SELECT word FROM filters WHERE id = '{cid}';")
        return r

    def add_filter(self, cid, key, caption="", file_id="", file_type=""):
        r = self.get_filter(cid, key)
        if r:
            self.conn.execute(
                f"""UPDATE filters SET
                    caption = '{caption}',
                    file_id = '{file_id}',
                    file_type = '{file_type}'
                WHERE
                    id = '{cid}' AND
                    word = '{key}';"""
            )
        else:
            self.conn.execute(
                f"""INSERT INTO filters VALUES (
                    '{cid}',
                    '{key}',
                    '{caption}',
                    '{file_id}',
                    '{file_type}'
                );"""
            )
        self.conn.save()

    def rem_filter(self, cid, key):
        self.conn.execute(
            f"DELETE FROM filters WHERE id = '{cid}' AND word = '{key}';"
        )
        self.conn.save()

    # Language
    def get_lang(self, cid):
        r = self.conn.execute(f"SELECT code FROM language WHERE id = '{cid}';")
        return r

    def set_lang(self, cid, lang):
        r = self.get_lang(cid)
        if r:
            self.conn.execute(
                f"""UPDATE language SET code = '{lang}'
                    WHERE id = '{cid}';"""
            )
        else:
            self.conn.execute(
                f"INSERT INTO language VALUES ('{cid}', '{lang}');"
            )
        self.conn.save()

    # Rules
    def get_rules(self, cid):
        r = self.conn.execute(f"SELECT rule FROM rules WHERE id = '{cid}';")
        return r

    def set_rules(self, cid, rules):
        rules = rules.replace("'", "''")
        r = self.get_rules(cid)
        if r:
            self.conn.execute(
                f"UPDATE FROM rules SET rule = '{rules}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(f"INSERT INTO rules VALUES ('{cid}', '{rules}')")
        self.conn.save()
