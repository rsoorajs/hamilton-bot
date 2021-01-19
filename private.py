async def handler(client, msg):
    client.select_lang(msg, "private")
    args = msg.text.split()
    command = args[0]
    args.remove(command)
    if command == "/start":
        await msg.reply(msg.lang["start"]["ok"])
