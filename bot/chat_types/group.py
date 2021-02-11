from time import time
from re import findall
from json import loads
from pyrogram.types import ChatPermissions
from chat_types import alltypes

# System of filters on groups
async def testfilters(client, msg):
    senders: dict = {
        "photo": client.send_photo,
        "sticker": client.send_sticker,
        "document": client.send_document,
        "audio": client.send_audio,
        "animation": client.send_animation,
        "voice": client.send_voice
    }
    text: str = msg.text
    filters = client.db.get_filters(msg.chat.id)
    for fname in filters:
        fname: str = fname[0]
        if not (
            (" " in fname and fname in text) or
            (fname in text.split())
          ):
            continue
        text, file_id, file_type = client.db.get_filter(msg.chat.id, fname)[0]
        if file_id:
            kwargs: dict = {
                "chat_id": msg.chat.id,
                "reply_to_message_id": msg.message_id
            }
            if text:
                kwargs["caption"]: str = text
            for k in senders.keys():
                if k == file_type:
                    send = senders[k]
                    kwargs[k]: int = file_id
                    if k == "sticker" and "caption" in kwargs:
                        kwargs.pop("caption")
                    break
            await send(**kwargs)
        elif text:
            await msg.reply(text)


# System no-flood
async def testflood(client, msg):
    cid: int = msg.chat.id
    uid: int = msg.from_user.id
    try:
        limit: int = client.db.get_flood(msg.chat.id)[0][0]
    except Exception:
        limit: int = 5
    if cid not in flood:
        flood[cid]: list = [uid, time(), msg.from_user.isadmin, 1]
    else:
        if (flood[cid][3] == (limit - 1)) and (flood[cid][0] == uid) and \
          (not flood[cid][2]):
            await ban(client, msg, [uid])
            flood.pop(cid)
        elif (time() - flood[cid][1]) <= 5 and flood[cid][0] == uid:
            flood[cid][3] += 1
        else:
            flood[cid]: list = [uid, time(), msg.from_user.isadmin, 1]


# Get id of user mentioned or with forwerd message
async def get_id(client, msg, args) -> int or None:
    if args:
        if type(args[0]) is int:
            uid: int = args[0]
        else:
            user = await client.get_chat(args[0])
            uid: int = user.id
    elif msg["reply_to_message"]:
        uid = msg.reply_to_message.from_user.id
    else:
        uid = None
    return uid


# Ban and unban of users
async def ban(client, msg, args):
    uid: int = await get_id(client, msg, args)
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
    uid: int = await get_id(client, msg, args)
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


async def setflood(client, msg, args):
    if not args:
        await msg.reply(msg.lang["setflood"]["no_limit"])
        return
    try:
        limit = int(args[0])
    except Exception:
        await msg.reply(msg.lang["setflood"]["need_number"])
        return
    if limit < 3:
        await msg.reply(msg.lang["setflood"]["minimium"])
        return
    try:
        client.db.set_flood(msg.chat.id, limit)
    except Exception:
        await msg.reply(msg.lang["setflood"]["failed"])
        return
    await msg.reply(msg.lang["setflood"]["ok"])


async def getflood(client, msg, args=None):
    limit = client.db.get_flood(msg.chat.id)
    if not limit:
        limit: int = 5
    else:
        limit: int = limit[0][0]
    await msg.reply(msg.lang["getflood"]["ok"].format(limit=limit))


async def addfilter(client, msg, args):
    kwargs: dict = {"cid": msg.chat.id}
    text_t: str = " ".join(args)
    key_t: list = findall("[\"|'].*[\"|']", text_t)
    if key_t:
        kwargs["key"]: str = key_t[0][1:-1]
        kwargs["caption"]: str = text_t.replace(key_t[0], "")
    elif len(text_t.split()) >= 1:
        kwargs["key"]: str = args[0]
        kwargs["caption"]: str = text_t.replace(args[0], "").strip()
    if msg.reply_to_message:
        reply = msg.reply_to_message
        if reply.text:
            kwargs["caption"]: str = reply.text
        elif reply.caption:
            kwargs["caption"]: str = reply.caption
        if reply.media:
            types = [
                "document", "sticker", "audio",
                "voice", "photo", "video", "animation"
            ]
            for ftype in types:
                if reply[ftype]:
                    kwargs["file_id"]: int = reply[ftype].file_id
                    kwargs["file_type"]: str = ftype
                    break
    if "key" not in kwargs:
        await msg.reply(msg.lang["addfilter"]["no_key"])
        return
    try:
        client.db.add_filter(**kwargs)
    except Exception:
        await msg.reply(msg.lang["addfilter"]["failed"])
        return
    await msg.reply(msg.lang["addfilter"]["ok"])


async def getfilters(client, msg, args=None):
    filters: list = client.db.get_filters(msg.chat.id)
    if not filters:
        await msg.reply(msg.lang["getfilters"]["no_filters"])
        return
    text: str = msg.lang["getfilters"]["ok"] + "\n\n"
    for filter_name in filters:
        text += "- `" + filter_name[0] + "`\n"
    await msg.reply(text)


async def remfilter(client, msg, args):
    if not args:
        await msg.reply(msg.lang["remfilter"]["no_filter"])
        return
    filter_name: str = args[0]
    client.db.rem_filter(msg.chat.id, filter_name)
    await msg.reply(msg.lang["remfilter"]["ok"])


async def kick(client, msg, args):
    uid: int = await get_id(client, msg, args)
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
    uid: str = msg.from_user.id
    try:
        await client.kick_chat_member(msg.chat.id, uid, until_date=5)
    except Exception:
        await msg.reply(msg.lang["kickme"]["failed"])
        return
    await msg.reply(msg.lang["kickme"]["ok"])


async def setrules(client, msg, args):
    text: str = ' '.join(args)
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
    rules: list = client.db.get_rules(msg.chat.id)
    if not rules:
        await msg.reply(msg.lang["rules"]["no_rules"])
    else:
        await msg.reply(rules[0][0])


async def mute(client, msg, args):
    uid: int = await get_id(client, msg, args)
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
            int(time() + 86400)
        )
    except Exception:
        await msg.reply(msg.lang["mute"]["failed"])
        return
    await msg.reply(msg.lang["mute"]["ok"])


async def unmute(client, msg, args):
    uid: int = await get_id(client, msg, args)
    if not uid:
        await msg.reply(msg.lang["unmute"]["no_user"])
        return
    permissions: dict = loads(str(msg.chat.permissions))
    permissions.pop("_")
    try:
        await client.restrict_chat_member(
            msg.chat.id,
            uid,
            ChatPermissions(**permissions)
        )
    except Exception:
        await msg.reply(msg.lang["unmute"]["failed"])
        return
    await msg.reply(msg.lang["unmute"]["ok"])


###########################
flood: dict = {}
for_administrator: dict = {
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
    "/unmute": unmute,
    "/setlang": alltypes.getlangs
}

for_all: dict = {
    "/start": lambda client, msg, args: msg.reply(msg.lang["start"]["ok"]),
    "/flood": getflood,
    "/filters": getfilters,
    "/kickme": kickme,
    "/rules": getrules,
    "/help": alltypes.help,
    "/channel": alltypes.channel,
    "/status": alltypes.status
}


async def handler(client, msg):
    if msg.left_chat_member:
        return
    client.select_lang(msg, "group")
    me = await client.get_chat_member(msg.chat.id, "me")
    me.isadmin: bool = me.status == "administrator"
    user = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    msg.from_user.isadmin: bool = user.status in ("administrator", "creator")
    if not msg.text:
        await testflood(client, msg)
        return
    args: list = msg.text.split(" ")
    command: str = args[0]
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
