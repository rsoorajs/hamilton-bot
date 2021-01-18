from time import time
from re import search

flood = {}
for_administrator = ["/ban", "/unban", "/setwelcome", "/setflood", "/addfilter", "/banall"]

async def handler(client, msg):
    if not msg.text:
        return
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
    elif command == "/banall":
        await banall(client, msg)
    elif command == "/unban":
        await unban(client, msg, args)
    elif command == "/setwelcome":
        await setwelcome(client, msg, args)
    elif command == "/setflood":
        await setflood(client, msg, args)
    elif command == "/flood":
        await getflood(client, msg)
    elif command == "/addfilter":
        await addfilter(client, msg, args)
    elif command == "/filters":
        await getfilters(client, msg)
    else:
        if not me.isadmin:
            await msg.reply("Eu não sou um administrador!")
            return
        await testfilters(client, msg)
        await testflood(client, msg)

async def testfilters(client, msg):
    filters = client.db.get_filters(msg.chat.id)
    for f in filters:
        if f[0] in msg.text:
            text, file_id, file_type = client.db.get_filter(msg.chat.id, f[0])[0]
            if file_id:
                kwargs = {"chat_id": msg.chat.id, "reply_to_message_id": msg.message_id}
                if text:
                    kwargs["caption"] = text
                if file_type == "photo":
                    send = client.send_photo
                    kwargs["photo"] = file_id
                elif file_type == "sticker":
                    send = client.send_sticker
                    kwargs["sticker"] = file_id
                    if "caption" in kwargs:
                        kwargs.pop("caption")
                elif file_type == "audio":
                    send = client.send_audio
                    kwargs["audio"] = file_id
                elif file_type == "voice":
                    send = client.send_voice
                    kwargs["voice"] = file_id
                elif file_type == "animation":
                    send = client.send_animation
                    kwargs["animation"] = file_id
                else:
                    send = client.send_document
                    kwargs["document"] = file_id
                    kwargs["force_document"] = True
                await send(**kwargs)
            elif text:
                await msg.reply(text)


async def testflood(client, msg):
    cid = msg.chat.id
    uid = msg.from_user.id
    try:
        limit = client.db.get_flood(msg.chat.id)[0][0]
    except:
        limit = 3
    if not cid in flood:
        flood[cid] = [uid, time(), msg.from_user.isadmin, 1]
    else:
        if flood[cid][3] == (limit - 1) and flood[cid][0] == uid and not flood[cid][2]:
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

# Ban && Unban
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

async def banall(client, msg):
    await msg.reply("Ok, banindo todo mundo!")
    async for member in client.iter_chat_members(msg.chat.id):
        if not member.status in ("administrator", "creator"):
            try:
                await client.kick_chat_member(msg.chat.id, member.user.id, until_date=5)
            except:
                pass
    await msg.reply("Ok, todo mundo foi removido!")

# Welcome
async def setwelcome(client, msg, args):
    if not args:
        await msg.reply("O que eu devo colocar como mensagem de boas vindas?")
        return
    try:
        client.db.set_welcome(msg.chat.id, " ".join(args))
    except:
        await msg.reply("Falha ao atualizar mensagem!")
        return
    await msg.reply("Ok, mensagem atualizada!")

# Flood
async def setflood(client, msg, args):
    if not args:
        await msg.reply("Quanto vai ser a quantia maxima?")
        return
    try:
        c = int(args[0])
    except:
        await msg.reply("Eu preciso de um número!")
        return
    try:
        client.db.set_flood(msg.chat.id, c)
    except Exception as error:
        print(error)
        await msg.reply("Falha ao definir limite!")
        return
    await msg.reply("Limite definido!")

async def getflood(client, msg):
    r = client.db.get_flood(msg.chat.id)
    if not r:
        r = 3
    else:
        r = r[0]
    await msg.reply(f"O limite atual é {r}.")

# Filter
async def addfilter(client, msg, args):
    kwargs = {"cid": msg.chat.id}
    text_t = " ".join(args)
    key_t = search("[\"|'].*[\"|\']", text_t)
    if "group" in dir(key_t):
        kwargs["key"] = key_t.group()[1:-1]
        kwargs["caption"] = text_t.replace(key_t.group(), "")
    elif len(text_t.split()) >= 1:
        kwargs["key"] = args[0]
        kwargs["caption"] = text_t.replace(args[0], "")
    if msg.reply_to_message:
        reply = msg.reply_to_message
        if reply.text:
            kwargs["caption"] = reply.text
        elif reply.caption:
            kwargs["caption"] = reply.caption
        if reply.media:
            for f in ["document", "sticker", "audio", "voice", "photo", "video", "animation"]:
                if reply[f]:
                    kwargs["file_id"] = reply[f].file_id
                    kwargs["file_type"] = f
                    break
    else:
        await msg.reply("Qual a chave para o filtro?")
        return
    try:
        client.db.add_filter(**kwargs)
    except Exception as error:
        print(error)
        await msg.reply("Falha ao adicionar filtro!")
        return
    await msg.reply("Filtro adicionado!")

async def getfilters(client, msg):
    r = client.db.get_filters(msg.chat.id)
    if not r:
        await msg.reply("Este grupo ainda não tem filtros!")
        return
    text = "Os seguintes filtros estão ativados:\n\n"
    for f in r:
        text += "- `" + f[0] + "`\n"
    await msg.reply(text)
