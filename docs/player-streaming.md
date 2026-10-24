# Player com streaming local

O player personalizado em `components/player.py` agora recebe uma URL local de
`services/video_stream.py`, em vez de inserir todo o MP4 como Base64 no HTML.

## Como funciona

- O Streamlit continua rodando normalmente com `streamlit run app.py`.
- Um servidor HTTP leve (biblioteca padrão do Python) começa ao abrir um vídeo.
- O servidor escuta **apenas em 127.0.0.1**, em uma porta local automática.
- O acesso ao MP4 usa um token aleatório na URL, sem divulgar caminhos do disco.
- Requisições `Range` retornam somente os bytes necessários, permitindo avanço
  na linha do tempo sem embutir o vídeo completo no HTML.
- As marcações, a legenda, o clique para saltar para um evento e os controles
  existentes no player HTML foram preservados.

**Limitação:** essa implementação é para uso LOCAL no mesmo computador em que
o Streamlit executa. Um visitante remoto, celular ou navegador em outra máquina
não consegue acessar o endereço 127.0.0.1 do servidor. Para implantação em rede
ou nuvem, será necessário servir os vídeos por um endpoint acessível ao cliente
(com autenticação e suporte a requisições Range). O acesso local também deve ser
protegido no próprio computador quando os vídeos forem sensíveis.

## Testes

Na raiz do projeto e com o ambiente virtual ativado:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
streamlit run app.py
```

Verifique visualmente: selecionar evento; iniciar no horário correto; reproduzir;
arrastar barra; clicar em marcações; conferir legenda; mudar entre vídeos.
Os testes de streaming usam bytes fictícios, sem dependências externas ou internet.

## Desempenho

O servidor transfere bytes em blocos de 256 KiB, em vez de construir um HTML
enorme com Base64. O navegador ainda pode baixar dados adicionais para
bufferização; não significa que somente o frame atual seja transferido.
O streaming não resolve limitações de codec MP4 no navegador.
