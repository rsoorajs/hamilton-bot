def create_table(name: str, **collumns) -> str:
    result: str = f"CREATE TABLE IF NOT EXISTS `{name}`("
    for collumn, types in collumns.items():
        result += f"{collumn} {types.upper()}, "
    result = result[:-2] + ");"
    return result


def insert(table: str, **collumns) -> str:
    part1: str = f"INSERT INTO `{table}`("
    part2: str = ") VALUES ("
    for collumn, value in collumns.items():
        if value is None:
            continue
        part1 += f"{collumn}, "
        part2 += f"'{value}', "
    query: str = part1[:-2] + part2[:-2] + ");"
    return query


def select(table: str, keys: list = ["*"], where: dict = {}) -> str:
    query: str = f"SELECT {', '.join(keys)} FROM `{table}`"
    if where:
        query += " WHERE "
        for collumn, value in where.items():
            query += f"{collumn} = '{value}' AND "
        query = query[:-5]
    query += ";"
    return query


def update(table: str, where: dict = {}, **collumns) -> str:
    query: str = f"UPDATE `{table}` SET "
    for collumn, value in collumns.items():
        if value is None:
            continue
        query += f"{collumn} = '{value}', "
    query = query[:-2]
    if where:
        query += " WHERE "
        for collumn, value in where.items():
            query += f"{collumn} = '{value}' AND "
        query = query[:-5]
    query += ";"
    return query


def delete(table: str, where: dict = {}) -> str:
    query: str = f"DELETE FROM `{table}`"
    if where:
        query += " WHERE "
        for collumn, value in where.items():
            query += f"{collumn} = '{value}' AND "
        query = query[:-5]
    query += ";"
    return query
