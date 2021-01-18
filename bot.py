from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import group
import private
import database

app = Client("Hamilton-bot")

app.db = database.crub(database.sqlite, file="banco.db")

@app.on_message(filters.new_chat_members)
async def new_members(client, msg):
    try:
        welcome = app.db.getwelcome(msg.chat.id)
    except:
        welcome = "Olá {first_name}, seja bem vindo!"
    chat = msg.chat
    for member in msg.new_chat_members:
        await client.send_message(
            chat.id,
            text=welcome.format(
                username = member.username,
                first_name = member.first_name,
                last_name = member.last_name,
                user_id = member.id,
                chat_name = chat.title,
                chat_id = chat.id
            )
        )

app.add_handler(MessageHandler(group.handler, filters.group))
app.add_handler(MessageHandler(private.handler, filters.private))

app.run()
