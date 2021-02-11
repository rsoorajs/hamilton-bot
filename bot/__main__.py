from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from chat_types import group, private
from json import load
from os import listdir, environ
from urllib.request import urlretrieve
# Bancos de dados
import mysql.connector
import database


configs: dict = {
    "CONFIG_URL": "config.ini",
    "BOT_CONFIG": "bot_config.json"
}

for config, file in configs.items():
    url: str or None = environ.get(config)
    if not url:
        continue
    print(f"Downloading {file} configuration file...")
    urlretrieve(url, filename=file)
    print("Complete")

app = Client("Hamilton-bot")
app.conf: dict = load(open("bot_config.json"))
app.db: database.crub = database.crub(
    mysql.connector.connect, **app.conf["mysql"]
)
app.langs: dict = {}
for fname in listdir("lang/"):
    dots: list = fname.split(".")
    if dots[-1] != "json":
        continue
    code: str = dots[0]
    app.langs[code]: dict = load(open("lang/"+fname))


def select_lang(msg, chat_type=None) -> str:
    lang: list = app.db.get_lang(msg.chat.id)
    if lang:
        code: str = lang[0][0]
    else:
        code: str = "pt-br"
    msg.lang: dict = app.langs[code]
    if chat_type:
        msg.lang: dict = msg.lang["commands"][chat_type]
    return code


app.select_lang = select_lang


@app.on_callback_query()
async def callback(client, msg) -> None:
    args: list = msg.data.split()
    command: str = args[0]
    args.pop(0)
    if command == "setlang":
        await client.all.setlang(client, msg, args)


@app.on_message(filters.new_chat_members)
async def new_members(client, msg) -> None:
    me = await client.get_me()
    client.select_lang(msg)
    try:
        welcome: str = app.db.getwelcome(msg.chat.id)[0][0]
    except Exception:
        welcome: str = msg.lang["default"]["welcome"]
    chat = msg.chat
    for member in msg.new_chat_members:
        if member.id == me.id:
            await client.send_message(chat.id, "Hello!")
            continue
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
