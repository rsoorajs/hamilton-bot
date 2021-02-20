from chat_types import alltypes

commands = {
    "/start": alltypes.start,
    "/setlang": alltypes.getlangs,
    "/help": alltypes.help,
    "/channel": alltypes.channel,
    "/status": alltypes.status,
    "/donate": alltypes.donate
}


async def handler(client, msg):
    client.select_lang(msg, "private")
    args: list = msg.text.split()
    command: str = args[0]
    args.remove(command)
    if command in commands:
        await commands[command](client, msg, args)
