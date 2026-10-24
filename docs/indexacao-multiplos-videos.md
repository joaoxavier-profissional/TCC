# Indexação de múltiplos vídeos — guia de uso e defesa

## Objetivo

Processar gravações MP4 individualmente com YOLO e OpenCV, transformar detecções por segundo em intervalos e persistir esses eventos no SQLite sem apagar outras gravações.

## Antes de começar

1. Faça **backup de `cftv.db`** antes da primeira indexação real.
2. Ative o ambiente `venv`, com OpenCV, Ultralytics e Streamlit já instalados.
3. Deixe os vídeos em `videos/` e os pesos `yolo11n.pt` na raiz do projeto.
4. Rode os testes antes de indexar. Eles não dependem de vídeo real nem de inferência YOLO.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python indexar_video.py teste.mp4
python indexar_video.py outro_video.mp4
streamlit run app.py
```

Use os nomes reais que aparecem na pasta `videos/`. **Não use `python criar_banco.py` sem informar o nome do vídeo.** Para importar manualmente o `eventos.csv`:

```bash
python criar_banco.py teste.mp4 --csv eventos.csv
```

## Pipeline

`indexar_video.py`: valida vídeo e pesos locais antes de começar; processa frames com YOLO (`classes=[0,2,3]`, `conf=0.40`); agrupa classes detectadas por segundo.

`services/indexacao.py`: reúne segundos adjacentes da mesma classe com lacuna de até dois segundos; escreve intervalos `HH:MM:SS` no SQLite.

`salvar_eventos()`: dentro de transação, apaga **somente os eventos do vídeo informado** e escreve os novos; se a inserção falhar, o banco reverte a transação. Um vídeo processado sem detecções terá zero eventos no banco. Outros vídeos não são alterados.

A interface `app.py` lê `cftv.db` e permite consultar os eventos de cada gravação.

## Limitações atuais

- A inferência pode ser lenta, dependendo da CPU/GPU, da duração e da resolução do vídeo.
- Processa todos os frames; não há paralelização nem barra de progresso.
- A indexação manual acontece no terminal, não pela interface.
- O evento descreve a **presença de uma classe**, não o acompanhamento de um indivíduo específico; duas pessoas simultâneas continuam contando como uma classe presente naquele segundo.
- Um intervalo de até dois segundos entre detecções da mesma classe é unido por heurística, não por rastreamento de objetos.
- `YOLO` usa pesos pré-treinados locais; nenhuma acurácia foi medida neste projeto ainda.
- A execução não faz download automático de pesos ausentes; se `yolo11n.pt` não estiver presente, o script informa o problema.
- Há um script legado `gerar_eventos.py` para CSV; o fluxo novo gera e grava eventos diretamente, sem CSV intermediário.
- Os scripts de indexação não devem ser executados simultaneamente no mesmo banco sem controle adicional de concorrência.

## Para justificar à banca

**Por que YOLO?** É uma arquitetura de detecção de objetos que permite inferência em frames com bibliotecas acessíveis em Python. Sua adequação concreta ao projeto precisa ser medida.

**Por que SQLite?** O protótipo utiliza um banco local embarcado, sem servidor de dados separado. Implantação em múltiplos computadores pode exigir revisão.

**Por que separar detecção, agrupamento e persistência?** Cada etapa resolve um problema independente e pode ser validada com testes isolados.

**Por que reindexar substitui somente o vídeo selecionado?** Garante atualização consistente desse vídeo sem apagar registros de outros arquivos.

**Próxima validação:** executar os testes, fazer backup do banco, indexar um dos MP4 adicionais e conferir se os eventos de `teste.mp4` continuam presentes.
