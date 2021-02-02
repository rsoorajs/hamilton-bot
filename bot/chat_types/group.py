from time import time
from re import search
from json import loads
from pyrogram.types import ChatPermissions


# Sistema de filtros dos chats
async def testfilters(client, msg):
    senders = {
        "photo": client.send_photo,
        "sticker": client.send_sticker,
        "document": client.send_document,
        "audio": client.send_audio,
        "animation": client.send_animation,
        "voice": client.send_voice
    }
    filters = client.db.get_filters(msg.chat.id)
    for f in filters:
        mtext = msg.text
        if not ((" " in f[0] and f[0] in mtext) or (f[0] in mtext.split())):
            continue
        text, file_id, file_type = client.db.get_filter(msg.chat.id, f[0])[0]
        if file_id:
            kwargs = {
                "chat_id": msg.chat.id,
                "reply_to_message_id": msg.message_id
            }
            if text:
                kwargs["caption"] = text
            for k in senders.keys():
                if k == file_type:
                    send = senders[k]
                    kwargs[k] = file_id
                    if k == "sticker" and "caption" in kwargs:
                        kwargs.pop("caption")
                    break
            await send(**kwargs)
        elif text:
            await msg.reply(text)


# Sistema anti-flood
async def testflood(client, msg):
    cid = msg.chat.id
    uid = msg.from_user.id
    try:
        limit = client.db.get_flood(msg.chat.id)[0][0]
    except Exception:
        limit = 5
    if cid not in flood:
        flood[cid] = [uid, time(), msg.from_user.isadmin, 1]
    else:
        if (flood[cid][3] == (limit - 1)) and (flood[cid][0] == uid) and \
          (not flood[cid][2]):
            await ban(client, msg, [uid])
            flood.pop(cid)
        elif (time() - flood[cid][1]) <= 5 and flood[cid][0] == uid:
            flood[cid][3] += 1
        else:
            flood[cid] = [uid, time(), msg.from_user.isadmin, 1]


# Função de obter id para evitar repetição de código em algumas partes
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


# Banimento e desbanimento de usuários
async def ban(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["ban"]["no_user"])
        return
    try:
        await client.kick_chat_member(msg.chat.id, uid)
    except Exception:
        await msg.reply(msg.lang["ban"]["failed"])
        return
    await msg.reply(msg.lang["ban"]["ok"])


async def unban(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["unban"]["no_user"])
        return
    try:
        await client.unban_chat_member(msg.chat.id, uid)
    except Exception:
        await msg.reply(msg.lang["unban"]["failed"])
        return
    await msg.reply(msg.lang["unban"]["ok"])


async def banall(client, msg, args=None):
    await msg.reply(msg.lang["banall"]["awaiting"])
    async for member in client.iter_chat_members(msg.chat.id):
        if member.status not in ("administrator", "creator"):
            try:
                await client.kick_chat_member(
                    msg.chat.id,
                    member.user.id,
                    until_date=5
                )
            except Exception:
                pass
    await msg.reply(msg.lang["banall"]["finish"])


# Bem vindo
async def setwelcome(client, msg, args):
    if not args:
        await msg.reply(msg.lang["setwelcome"]["no_message"])
        return
    try:
        client.db.set_welcome(msg.chat.id, " ".join(args))
    except Exception:
        await msg.reply(msg.lang["setwelcome"]["failed"])
        return
    await msg.reply(msg.lang["setwelcome"]["ok"])


# Sistema de controle de flood
async def setflood(client, msg, args):
    if not args:
        await msg.reply(msg.lang["setflood"]["no_limit"])
        return
    try:
        c = int(args[0])
    except Exception:
        await msg.reply(msg.lang["setflood"]["need_number"])
        return
    if c < 3:
        await msg.reply(msg.lang["setflood"]["minimium"])
        return
    try:
        client.db.set_flood(msg.chat.id, c)
    except Exception as error:
        print(error)
        await msg.reply(msg.lang["setflood"]["failed"])
        return
    await msg.reply(msg.lang["setflood"]["ok"])


async def getflood(client, msg, args=None):
    r = client.db.get_flood(msg.chat.id)
    if not r:
        r = 5
    else:
        r = r[0][0]
    await msg.reply(msg.lang["getflood"]["ok"].format(limit=r))


# Filtros de mensagens
async def addfilter(client, msg, args):
    kwargs = {"cid": msg.chat.id}
    text_t = " ".join(args)
    key_t = search("[\"|'].*[\"|']", text_t)
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
            types = [
                    "document", "sticker", "audio",
                    "voice", "photo", "video", "animation"
                ]
            for f in types:
                if reply[f]:
                    kwargs["file_id"] = reply[f].file_id
                    kwargs["file_type"] = f
                    break
    if "key" not in kwargs:
        await msg.reply(msg.lang["addfilter"]["no_key"])
        return
    try:
        client.db.add_filter(**kwargs)
    except Exception as error:
        print(error)
        await msg.reply(msg.lang["addfilter"]["failed"])
        return
    await msg.reply(msg.lang["addfilter"]["ok"])


async def getfilters(client, msg, args=None):
    r = client.db.get_filters(msg.chat.id)
    if not r:
        await msg.reply(msg.lang["getfilters"]["no_filters"])
        return
    text = msg.lang["getfilters"]["ok"] + "\n\n"
    for f in r:
        text += "- `" + f[0] + "`\n"
    await msg.reply(text)


async def remfilter(client, msg, args):
    if not args:
        await msg.reply(msg.lang["remfilter"]["no_filter"])
        return
    f = args[0]
    client.db.rem_filter(msg.chat.id, f)
    await msg.reply(msg.lang["remfilter"]["ok"])


# Saída temporária de um grupo
async def kick(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["kick"]["no_user"])
        return
    try:
        await client.kick_chat_member(msg.chat.id, uid, until_date=5)
    except Exception:
        await msg.reply(msg.long["kick"]["failed"])
        return
    await msg.reply(msg.lang["kick"]["ok"])


async def kickme(client, msg, args):
    if msg.from_user.isadmin:
        await msg.reply(msg.lang["kickme"]["admin"])
        return
    uid = msg.from_user.id
    try:
        await client.kick_chat_member(msg.chat.id, uid, until_date=5)
    except Exception:
        await msg.reply(msg.lang["kickme"]["failed"])
        return
    await msg.reply(msg.lang["kickme"]["ok"])


# Regras
async def setrules(client, msg, args):
    text = ' '.join(args)
    if not text:
        await msg.reply(msg.lang["setrules"]["no_rules"])
        return
    try:
        client.db.set_rules(msg.chat.id, text)
    except Exception:
        await msg.reply(msg.lang["setrules"]["failed"])
        return
    await msg.reply(msg.lang["setrules"]["ok"])


async def getrules(client, msg, args):
    r = client.db.get_rules(msg.chat.id)
    if not r:
        await msg.reply(msg.lang["rules"]["no_rules"])
    else:
        await msg.reply(r[0][0])


# Silenciar
async def mute(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["mute"]["no_user"])
        return
    user = await client.get_chat_member(msg.chat.id, uid)
    user.isadmin = user.status in ("administrator", "creator")
    if user.isadmin:
        await msg.reply(msg.lang["mute"]["admin"])
        return
    try:
        await client.restrict_chat_member(
            msg.chat.id,
            uid,
            ChatPermissions(),
            int(time() + 2073600)
        )
    except Exception:
        await msg.reply(msg.lang["mute"]["failed"])
        return
    await msg.reply(msg.lang["mute"]["ok"])


async def unmute(client, msg, args):
    uid = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["unmute"]["no_user"])
        return
    permissions = loads(str(msg.chat.permissions))
    permissions.pop("_")
    try:
        await client.restrict_chat_member(
            msg.chat.id,
            uid,
            ChatPermissions(**permissions)
        )
    except Exception as error:
        print(error)
        await msg.reply(msg.lang["unmute"]["failed"])
        return
    await msg.reply(msg.lang["unmute"]["ok"])


#######################################
# Sistema de verificação dos comandos #
#######################################
flood = {}
for_administrator = {
    "/ban": ban,
    "/unban": unban,
    "/banall": banall,
    "/setwelcome": setwelcome,
    "/setflood": setflood,
    "/addfilter": addfilter,
    "/remfilter": remfilter,
    "/kick": kick,
    "/setrules": setrules,
    "/mute": mute,
    "/unmute": unmute
}

for_all = {
    "/start": lambda client, msg, args: msg.reply(msg.lang["start"]["ok"]),
    "/flood": getflood,
    "/filters": getfilters,
    "/kickme": kickme,
    "/rules": getrules
}


async def handler(client, msg):
    if msg.left_chat_member:
        return
    client.select_lang(msg, "group")
    for_administrator["/setlang"] = client.all.getlangs
    for_all["/help"] = client.all.help
    for_all["/channel"] = client.all.channel
    for_all["/status"] = client.all.status
    me = await client.get_chat_member(msg.chat.id, "me")
    me.isadmin = me.status == "administrator"
    user = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    msg.from_user.isadmin = user.status in ("administrator", "creator")
    if not msg.text:
        await testflood(client, msg)
        return
    args = msg.text.split()
    command = args[0]
    args.remove(command)
    if command in for_administrator:
        if not msg.from_user.isadmin:
            await msg.reply(msg.lang["no_admin"]["you"])
            return
        await for_administrator[command](client, msg, args)
    elif command in for_all:
        await for_all[command](client, msg, args)
    else:
        await testfilters(client, msg)
    client.select_lang(msg, "group")
    if not me.isadmin:
        await msg.reply(msg.lang["no_admin"]["me"])
        return
    await testflood(client, msg)
