Instalação
==========

Instalando e rodando o bot em um sistema operacional linux ou macOS usando o terminal.

Primeiramente instale o python 3.6 ou superior;

  - Clone o repositório do github e entre na pasta;
  - Rode `pip3 install -r requirements.txt` para instalar as bibliotecas precisas;
  - Agora configure o pyrogram de acordo com o que está no [readme](https://github.com/dheisom-gomes/hamilton-bot) do repositório;
  - Execute o bot com `python3 bot` e pronto.

Para execução em ambiente ssh só é preciso o uso do comando `nohup`(depois da Instalação), um exemplo: `nohup python3 bot &`;

Se for usar no Heroku é só configurar as variáveis de ambiente e subir os arquivos que já vai funcionar.
