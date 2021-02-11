from chat_types import alltypes

commands = {
    "/start": lambda client, msg, args: msg.reply(msg.lang["start"]["ok"]),
    "/setlang": alltypes.getlangs,
    "/help": alltypes.help,
    "/channel": alltypes.channel,
    "/status": alltypes.status
}


async def handler(client, msg):
    client.select_lang(msg, "private")
    args: list = msg.text.split()
    command: str = args[0]
    args.remove(command)
    if command in commands:
        await commands[command](client, msg, args)
