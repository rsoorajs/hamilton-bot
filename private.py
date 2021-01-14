async def handler(client, msg):
    args = msg.text.split()
    command = args[0]
    args.remove(command)
    if command == "/start":
        await msg.reply("Olá, sou um bot de administração de grupos para telegram e estou em desenvolvimento.")
