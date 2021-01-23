from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def help(client, msg, args):
    client.select_lang(msg, "all")
    await msg.reply(msg.lang["help"]["ok"])


# Escolha e lista de linguagens
async def setlang(client, msg, args):
    msg = msg.message
    client.select_lang(msg, "all")
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
