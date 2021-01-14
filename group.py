from time import time

flood = {}
for_administrator = ["/ban", "/unban"]

async def handler(client, msg):
    args = msg.text.split()
    command = args[0]
    args.remove(command)
    me = await client.get_chat_member(msg.chat.id, "me")
    me.isadmin = me.status == "administrator"
    user = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    msg.from_user.isadmin = user.status in ("administrator", "creator")
    if command in for_administrator and not msg.from_user.isadmin:
        await msg.reply("Você não é um administrador!")
        return
    elif command in for_administrator and not me.isadmin:
        await msg.reply("Eu não sou um administrador!")
        return
    if command == "/start":
        await msg.reply("Olá, posso administrar esse grupo, para isso você só precisa me dar admin e me configurar.")
    elif command == "/ban":
        await ban(client, msg, args)
    elif command == "/unban":
        await unban(client, msg, args)
    else:
        cid = msg.chat.id
        uid = msg.from_user.id
        if not cid in flood:
            flood[cid] = [uid, time(), msg.from_user.isadmin, 1]
        else:
            if flood[cid][3] == 4 and flood[cid][0] == uid and not flood[cid][2]:
                await ban(client, msg, [uid])
                flood.pop(cid)
            elif (time() - flood[cid][1]) <= 5 and flood[cid][0] == uid:
                flood[cid][3] += 1
            else:
                flood[cid] = [uid, time(), msg.from_user.isadmin, 1]

async def get_id(client, msg, args):
    if args:
        if type(args[0]) is int:
            uid = args[0]
        else:
            user = await client.get_chat(args[0])
            uid = user.id
    elif msg["reply_to_message"]:
        uid = msg.reply_to_message.from_user.id
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
