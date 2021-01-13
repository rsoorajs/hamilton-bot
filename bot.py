from pyrogram import Client

app = Client("Hamilton-bot")

@app.on_message()
async def handler(client, msg):
    print(msg.text)
    await msg.reply(msg.text.upper())

app.run()
