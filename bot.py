from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from json import load
from os import listdir
import group
import private
import database

app = Client("Hamilton-bot")
app.db = database.crub(database.sqlite, file="banco.db")
app.langs = {}
for fname in listdir("lang/"):
    code = fname.split(".")[0]
    app.langs[code] = load(open("lang/"+fname))


def select_lang(msg, chat_type=None):
    lang = app.db.get_lang(msg.chat.id)
    if lang:
        code = lang[0][0]
    else:
        code = "pt-br"
    msg.lang = app.langs[code]
    if chat_type:
        msg.lang = msg.lang["commands"][chat_type]
    return code


app.select_lang = select_lang


@app.on_message(filters.new_chat_members)
async def new_members(client, msg):
    client.select_lang(msg)
    try:
        welcome = app.db.getwelcome(msg.chat.id)
    except Exception:
        welcome = msg.lang["default"]["welcome"]
    chat = msg.chat
    for member in msg.new_chat_members:
        await client.send_message(
            chat.id,
            text=welcome.format(
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name,
                user_id=member.id,
                chat_name=chat.title,
                chat_id=chat.id
            )
        )

app.add_handler(MessageHandler(group.handler, filters.group))
app.add_handler(MessageHandler(private.handler, filters.private))

app.run()
