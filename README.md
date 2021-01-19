# !! Atenção !!

Esté projeto ainda está em construção no meu canal no youtube, daqui alguns dias ele estará pronto para uso em grupos grandes.

# Instalação das dependências

Para instalar as dependências é simples, você só precisa executar `pip3 install -r  requirements.txt`, se não for é só rodar com `sudo` no começo.

# Como configurar

Você deve ir no site [My Telegram] e abrir a aba "API Development tools" e fazer o registro de um APP para poder pegar a `api_id` e `api_hash`, depois pegue o token do seu bot em [@BotFatcher] para adicionar no arquivo `config.ini`, crie ele da seguinte forma:

```ini
[pyrogram]
api_id = idDoSeuApp
api_hash = hashDoSeuApp
bot_token = oTokenDoBot
```

E pronto, agora é só iniciar o bot!

[My Telegram]: <https://my.telegram.org>
[@BotFatcher]: <https://t.me/BotFather>