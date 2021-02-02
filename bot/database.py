def create_table(name: str, **kwargs) -> str:
    result: str = f"CREATE TABLE IF NOT EXISTS `{name}`("
    for key in kwargs.keys():
        result += f"{key} {str(kwargs[key]).upper()}, "
    result = result[:-2] + ");"
    return result


class connect:
    connection = None
    cursor = None

    def __init__(self, func, database=None, *args, **kwargs):
        self.connector = func
        self.login: list = [args, kwargs]
        self.database: str or None = database
        self.db = self.connect()

    def connect(self) -> None:
        self.connection = self.connector(*self.login[0], **self.login[1])
        self.cursor = self.connection.cursor()
        if "autocommit" in dir(self.connection):
            self.connection.autocommit: bool = True
        if self.database:
            self.cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.database}` DEFAULT \
                CHARSET utf8 COLLATE = utf8_general_ci;"
            )
            self.cursor.execute(f"USE `{self.database}`;")

    def close(self) -> None:
        self.connection.close()

    def save(self) -> None:
        try:
            self.connection.commit()
            self.connection.disconnect()
        except Exception:
            pass
        self.close()
        self.connect()

    def execute(self, cmd: str, error: bool = False) -> list:
        try:
            self.connection.ping()
            self.cursor.execute(cmd)
        except Exception as err:
            if error:
                raise err
            self.save()
            self.execute(cmd, error=True)
        try:
            result: list = self.cursor.fetchall()
        except Exception:
            result: list = []
        return result


class crub:
    def __init__(self, sql, database=None, *args, **kwargs):
        self.conn = connect(sql, database, *args, **kwargs)
        if database:
            self.conn.execute(f"USE {database};")
        self.conn.execute(create_table("flood", id="bigint", amount="bigint"))
        self.conn.execute(create_table("welcome", id="bigint", hello="text"))
        self.conn.execute(
            create_table(
                "filters",
                id="bigint",
                word="text",
                caption="text",
                file_id="text",
                file_type="text"
            )
        )
        self.conn.execute(create_table("language", id="bigint", code="text"))
        self.conn.execute(create_table("rules", id="bigint", rule="text"))
        self.conn.save()

    # Welcome
    def get_welcome(self, cid: int) -> list:
        result: list = self.conn.execute(
            f"SELECT hello FROM welcome WHERE id = '{cid}';"
        )
        return result

    def set_welcome(self, cid: int, text: str) -> None:
        welcome: list = self.get_welcome(cid)
        if welcome:
            self.conn.execute(
                f"UPDATE welcome SET hello = '{text}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(
                f"INSERT INTO welcome VALUES ('{cid}', '{text}');"
            )
        self.conn.save()

    # Flood
    def get_flood(self, cid: int) -> list:
        result: list = self.conn.execute(
            f"SELECT amount FROM flood WHERE id = '{cid}';"
        )
        return result

    def set_flood(self, cid: int, limit: int) -> None:
        flood = self.get_flood(cid)
        if flood:
            self.conn.execute(
                f"UPDATE flood SET amount = '{limit}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(
                f"INSERT INTO flood VALUES ('{cid}', '{limit}');"
            )
        self.conn.save()

    # Filter
    def get_filter(self, cid, key) -> list:
        result: list = self.conn.execute(
            f"""SELECT caption, file_id, file_type FROM filters
            WHERE
                id = '{cid}' AND
                word = '{key}';"""
        )
        return result

    def get_filters(self, cid) -> None:
        filters = self.conn.execute(
            f"SELECT word FROM filters WHERE id = '{cid}';"
        )
        return filters

    def add_filter(self, cid: int, key: str, caption: str = "",
                   file_id: str = "", file_type: int = "") -> None:
        old_filter: list = self.get_filter(cid, key)
        if old_filter:
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

    def rem_filter(self, cid: int, key: str) -> None:
        self.conn.execute(
            f"DELETE FROM filters WHERE id = '{cid}' AND word = '{key}';"
        )
        self.conn.save()

    # Language
    def get_lang(self, cid: int) -> list:
        result: list = self.conn.execute(
            f"SELECT code FROM language WHERE id = '{cid}';"
        )
        return result

    def set_lang(self, cid: int, lang: str) -> None:
        old_lang: list = self.get_lang(cid)
        if old_lang:
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
    def get_rules(self, cid: int) -> list:
        result: list = self.conn.execute(
            f"SELECT rule FROM rules WHERE id = '{cid}';"
        )
        return result

    def set_rules(self, cid: int, rules: str) -> None:
        rules = rules.replace("'", "''")
        old_rules: list = self.get_rules(cid)
        if old_rules:
            self.conn.execute(
                f"UPDATE FROM rules SET rule = '{rules}' WHERE id = '{cid}';"
            )
        else:
            self.conn.execute(f"INSERT INTO rules VALUES ('{cid}', '{rules}')")
        self.conn.save()
