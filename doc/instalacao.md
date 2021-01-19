Instalação
==========

Instalando e rodando o bot em um sistema operacional linux ou macOS através do terminal.

Primeiramente instale o python 3.6 ou maior;

  - Clone o repositório do github e entre na pasta;
  - Rode `pip3 install -r requirements.txt` para instalar as bibliotecas precisas;
  - Agora configure o pyrogram de acordo com o que está no [readme](https://github.com/dheisom-gomes/hamilton-bot) do repositório;
  - Execute o arquivo `bot.py` com `python3 bot.py` e pronto.

Para execução em ambiente ssh só é preciso o uso do comando `nohup`, um exemplo: `nohup python3 bot.py &`(testado no linux)