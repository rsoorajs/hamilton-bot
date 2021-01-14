async def handler(client, msg):
    args = msg.text.split()
    command = args[0]
    args.remove(command)
    if command == "/start":
        await msg.reply("Olá, posso administrar esse grupo, para isso você só precisa me dar admin e me configurar.")
    elif command == "/ban":
        await ban(client, msg, args)
    elif command == "/unban":
        await unban(client, msg, args)

async def get_id(client, msg, args):
    if msg["reply_to_message"]:
        uid = msg.reply_to_message.from_user.id
    elif args:
        user = await client.get_chat(args[0])
        uid = user.id
    else:
        uid = None
    return uid

async def ban(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply("Quem eu devo banir? :)")
        return
    try:
        await client.kick_chat_member(msg.chat.id, uid)
    except:
        await msg.reply("Falha ao banir usuário!")
        return
    await msg.reply("Usuário banido!")

async def unban(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply("Quem eu devo desbanir?")
        return
    try:
        await client.unban_chat_member(msg.chat.id, uid)
    except:
        await msg.reply("Deu falha ao desbanir!")
        return
    await msg.reply("Usuário desbanido!")
