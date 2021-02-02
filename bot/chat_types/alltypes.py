from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import psutil


async def help(client, msg, args):
    client.select_lang(msg, "all")
    await msg.reply(msg.lang["help"]["ok"])


# Escolha e lista de linguagens
# - Callback de resposta
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


# - Envia a lista de botões com os idiomas
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


async def channel(client, msg, args):
    client.select_lang(msg, "all")
    if "channel" in client.conf:
        await msg.reply(
            msg.lang["channel"]["ok"].format(uri=client.conf["channel"])
        )


async def status(client, msg, args):
    cpu = psutil.cpu_freq()
    cpu_str = f"{int(cpu.current)}/{int(cpu.max)}MHZ ({psutil.cpu_percent()}%)"
    mem = psutil.virtual_memory()
    mem_str = f"{mem.used // 1048576}/{mem.total // 1048576}MiB"
    mem_str += f" ({int((mem.used / mem.total) * 100)}%)"
    await msg.reply(
        "Server status\n" +
        f"Memory: {mem_str}\n" +
        f"CPU[min={int(cpu.min)}MHZ]: {cpu_str}"
    )
