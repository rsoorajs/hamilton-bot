from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import group
import private

app = Client("Hamilton-bot")

@app.on_message(filters.new_chat_members)
async def new_members(client, msg):
    for member in msg.new_chat_members:
        await client.send_message(msg.chat.id, text=f"Olá {member.first_name}, seja bem vindo!")

app.add_handler(MessageHandler(group.handler, filters.group))
app.add_handler(MessageHandler(private.handler, filters.private))

app.run()
