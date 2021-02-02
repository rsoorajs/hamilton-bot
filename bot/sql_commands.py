def create_table(name: str, **kwargs) -> str:
    result: str = f"CREATE TABLE IF NOT EXISTS `{name}`("
    for key in kwargs.keys():
        result += f"{key} {str(kwargs[key]).upper()}, "
    result = result[:-2] + ");"
    return result


def insert(table: str, **kwargs) -> str:
    part1 = f"INSERT INTO `{table}`("
    part2 = ") VALUES ("
    for key in kwargs.keys():
        part1 += f"{key}, "
        part2 += f"'{kwargs[key]}', "
    query = part1[:-2] + part2[:-2] + ");"
    return query


def select(table: str, keys: list = ["*"], where: dict = {}) -> str:
    query = "SELECT (" + ", ".join(keys) + f") FROM `{table}`"
    if where:
        query += " WHERE "
        for collumn in where.keys():
            query += f"{collumn} = '{where[collumn]}', "
        query = query[:-2]
    query += ";"
    return query


def update(table: str, where: dict = {}, **collumns) -> str:
    query = f"UPDATE `{table}` SET "
    for collumn, value in zip(collumns.keys(), collumns.values()):
        query += f"{collumn} = '{value}' AND "
    query = query[:-5]
    if where:
        query += " WHERE "
        for collumn in where.keys():
            query += f"{collumn} = '{where[collumn]}' AND "
        query = query[:-5]
    query += ";"
    return query


def delete(table: str, where: dict = {}) -> str:
    query = f"DELETE FROM `{table}`"
    if where:
        query += " WHERE "
        for key, value in zip(where.keys(), where.values()):
            query += f"{key} = '{value}' AND "
        query = query[:-5]
    query += ";"
    return query
