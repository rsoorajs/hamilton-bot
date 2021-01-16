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
        except:
            r = []
        return r

class crub:
    def __init__(self, sql, database=None,  **kwargs):
        self.conn = sql(**kwargs)
        if database:
            self.conn.execute(f"USE {database};")
        self.conn.execute("CREATE TABLE IF NOT EXISTS flood(id INTEGER, amount INTEGER);")
        self.conn.execute("CREATE TABLE IF NOT EXISTS welcome(id INTEGER, hello TEXT);")
        self.conn.save()

    def setwelcome(self, cid, text):
        r = self.conn.execute(f"SELECT * FROM welcome WHERE id = '{cid}';")
        if r:
            self.conn.execute(f"UPDATE welcome SET hello = '{text}' WHERE id = '{cid}';")
        else:
            self.conn.execute(f"INSERT INTO welcome VALUES ('{cid}', '{text}');")
        self.conn.save()

    def getwelcome(self, cid):
        r = self.conn.execute(f"SELECT (hello) FROM welcome WHERE id = '{cid}';")[0][0]
        return r

    def setflood(self, cid, limit):
        r = self.conn.execute(f"SELECT * FROM flood WHERE id = '{cid}';")
        if r:
            self.conn.execute(f"UPDATE flood SET amount = '{limit}' WHERE id = '{cid}';")
        else:
            self.conn.execute(f"INSERT INTO flood VALUES ('{cid}', '{limit}');")
        self.conn.save()

    def getflood(self, cid):
        r = self.conn.execute(f"SELECT (amount) FROM flood WHERE id = '{cid}';")[0]
        return r
