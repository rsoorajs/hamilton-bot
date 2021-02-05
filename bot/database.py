from sql_commands import create_table, insert, delete, update, select


class connect:
    connection = None
    cursor = None

    def __init__(self, func, database=None, *args, **kwargs):
        self.connector = func
        self.login: list = [args, kwargs]
        self.database: str = database
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
        self.conn.execute(
            create_table(
                "flood",
                id="bigint not null",
                amount="int(10) not null"
            )
        )
        self.conn.execute(
            create_table(
                "welcome",
                id="bigint not null",
                hello="varchar(4096) not null"
            )
        )
        self.conn.execute(
            create_table(
                "filters",
                id="bigint not null",
                word="text not null",
                caption="text not null",
                file_id="text",
                file_type="text"
            )
        )
        self.conn.execute(
            create_table(
                "language",
                id="bigint not null",
                code="varchar(10) not null"
            )
        )
        self.conn.execute(
            create_table(
                "rules",
                id="bigint",
                rule="varchar(4096) not null"
            )
        )
        self.conn.save()

    # Welcome
    def get_welcome(self, cid: int) -> list:
        result: list = self.conn.execute(
            select("hello", ["welcome"], {"id": cid})
        )
        return result

    def set_welcome(self, cid: int, text: str) -> None:
        welcome: list = self.get_welcome(cid)
        if welcome:
            self.conn.execute(update("welcome", {"id": cid}, hello=text))
        else:
            self.conn.execute(insert("welcome", id=cid, hello=text))
        self.conn.save()

    # Flood
    def get_flood(self, cid: int) -> list:
        result: list = self.conn.execute(
            select("flood", ["amount"], {"id": cid})
        )
        return result

    def set_flood(self, cid: int, limit: int) -> None:
        flood: list = self.get_flood(cid)
        if flood:
            self.conn.execute(update("flood", {"id": cid}, amount=limit))
        else:
            self.conn.execute(insert("flood", id=cid, amount=limit))
        self.conn.save()

    # Filter
    def get_filter(self, cid, key) -> list:
        result: list = self.conn.execute(
            select("filters", ["caption", "file_id", "file_type"],
                   {"id": cid, "word": key})
        )
        return result

    def get_filters(self, cid) -> None:
        filters: list = self.conn.execute(
            select("filters", ["word"], {"id": cid})
        )
        return filters

    def add_filter(self, cid: int, key: str, caption: str = None,
                   file_id: str = None, file_type: int = None) -> None:
        old_filter: list = self.get_filter(cid, key)
        if old_filter:
            self.conn.execute(
                update(
                    "filters",
                    {"id": cid, "word": key},
                    caption=caption,
                    file_id=file_id,
                    file_type=file_type
                )
            )
        else:
            self.conn.execute(
                insert(
                    "filters",
                    id=cid,
                    word=key,
                    caption=caption,
                    file_id=file_id,
                    file_type=file_type
                )
            )
        self.conn.save()

    def rem_filter(self, cid: int, key: str) -> None:
        self.conn.execute(delete("filters", {"id": cid, "word": key}))
        self.conn.save()

    # Language
    def get_lang(self, cid: int) -> list:
        result: list = self.conn.execute(
            select("language", ["code"], {"id": cid})
        )
        return result

    def set_lang(self, cid: int, lang: str) -> None:
        old_lang: list = self.get_lang(cid)
        if old_lang:
            self.conn.execute(update("language", {"id": cid}, code=lang))
        else:
            self.conn.execute(insert("language", id=cid, code=lang))
        self.conn.save()

    # Rules
    def get_rules(self, cid: int) -> list:
        result: list = self.conn.execute(
            select("rules", ["rule"], {"id": cid})
        )
        return result

    def set_rules(self, cid: int, rules: str) -> None:
        rules = rules.replace("'", "''")
        old_rules: list = self.get_rules(cid)
        if old_rules:
            self.conn.execute(update("rules", {"id": cid}, rule=rules))
        else:
            self.conn.execute(insert("rules", id=cid, rule=rules))
        self.conn.save()
