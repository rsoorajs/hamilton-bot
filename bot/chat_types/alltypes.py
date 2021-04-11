from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import psutil


async def help(client, msg, args):
    client.select_lang(msg, "all")
    await msg.reply(msg.lang["help"]["ok"])

async def start(client, msg, args):
    client.select_lang(msg, "all")
    await msg.reply(msg.lang["start"]["ok"])

# Choose of languages
# - Callback of response
async def setlang(client, callback, args):
    msg = callback.message
    client.select_lang(msg, "all")
    if msg.chat.type in ("group", "supergroup"):
        info = await client.get_chat_member(msg.chat.id, callback.from_user.id)
        if info.status not in ("administrator", "creator"):
            await client.answer_callback_query(
                callback.id,
                msg.lang["setlang"]["not_admin"],
                show_alert=True
            )
            return
    if not args[0] in client.langs:
        await client.edit_message_text(
            message_id=msg.message_id,
            chat_id=msg.chat.id,
            text=msg.lang["setlang"]["not_found"]
        )
        return
    client.db.set_lang(msg.chat.id, args[0])
    client.select_lang(msg, "all")
    await client.edit_message_text(
        message_id=msg.message_id,
        chat_id=msg.chat.id,
        text=msg.lang["setlang"]["ok"]
    )
    await client.answer_callback_query(callback.id, "Ok.")


# - Send buttons to choose a language
async def getlangs(client, msg, args):
    client.select_lang(msg, "all")
    text = msg.lang["setlang"]["select"] + "\n\n"
    buttons = []
    for lang in client.langs.keys():
        buttons.append(
            [
                InlineKeyboardButton(
                    client.langs[lang]["name"]+" - "+lang,
                    callback_data="setlang " + lang
                )
            ]
        )
    await msg.reply(text, reply_markup=InlineKeyboardMarkup(buttons))


# Channel of updates from bot
async def channel(client, msg, args):
    client.select_lang(msg, "all")
    if "channel" in client.conf:
        await msg.reply(
            msg.lang["channel"]["ok"].format(uri=client.conf["channel"])
        )


# Stats of server computer
async def status(client, msg, args):
    cpu = psutil.cpu_freq()
    cpu_str: str = f"{int(cpu.current)}/{int(cpu.max)}MHZ ({psutil.cpu_percent()}%)"
    mem = psutil.virtual_memory()
    mem_str: str = f"{mem.used // 1048576}/{mem.total // 1048576}MiB"
    mem_str += f" ({int((mem.used / mem.total) * 100)}%)"
    disk = psutil.disk_usage(".")
    disk_str: str = f"{disk.used // (2**30)}/{disk.total // (2**30)}GiB"
    disk_str += f" ({int(disk.percent)}%)"
    await msg.reply(
        "Server status\n\n" +
        f"Memory: {mem_str}\n" +
        f"CPU[min={int(cpu.min)}MHZ]: {cpu_str}\n" +
        f"Disk: {disk_str}"
    )
