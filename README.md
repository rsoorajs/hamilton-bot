# !! Atenção !!

**Esté projeto ainda está em construção e não deve ser usado em grupos grandes.**

# Instalação das dependências

Para instalar as dependências é simples, você só precisa executar `pip3 install -r  requirements.txt`, se não for é só rodar com `sudo` no começo.

# Como configurar e rodar o bot?

Você deve ir no site [My Telegram] e abrir a aba "API Development tools" e fazer o registro de um APP para poder pegar a `api_id` e `api_hash`, depois pegue o token do seu bot em [@BotFather] para adicionar em um arquivo `ini`, crie ele da seguinte forma:

```ini
[pyrogram]
api_id = idDoSeuApp
api_hash = hashDoSeuApp
bot_token = oTokenDoBot
```

E depois fazer upload do arquivo para algum lugar que tenha link de download direto sem ir para uma página, veja um exemplo com o termbin.com no linux:

```bash
$ cat config.ini | nc termbin.com 9999
```

E depois crie a variável de ambiente `CONFIG_URL` com a url do arquivo execute o script `bot.py`, veja um exemplo no linux:

```bash
$ export CONFIG_URL=https://example.com/config.ini
$ python3 bot.py
```

E pronto, você já pode usar o bot!

[My Telegram]: <https://my.telegram.org>
[@BotFather]: <https://t.me/BotFather>
