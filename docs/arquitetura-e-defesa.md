# Arquitetura técnica — TCC CFTV

> **Estado:** documento inicial de estudo, baseado nos arquivos inspecionados na branch `melhoria/player-streaming-local` em outubro de 2026. Não substitui testes de integração ou a descrição do pipeline de detecção por IA ainda não verificado no repositório.

## 1. Objetivo observado

O aplicativo oferece navegação por gravações MP4, consulta de eventos indexados, reprodução em horários específicos e relatórios dos registros. A interface descreve-se como “Sistema inteligente de indexação e recuperação de eventos em gravações de CFTV”.

## 2. Visão dos módulos

```text
app.py (inicialização, estado e navegação Streamlit)
  ├── components/sidebar.py (menu)
  ├── views/visao_geral.py (dashboard)
  ├── views/buscar_eventos.py (formulário + resultados)
  │     ├── services/busca.py (regras de filtragem/ordenação)
  │     └── components/player.py (HTML e JavaScript)
  │             └── services/video_stream.py (servidor HTTP local + Range)
  ├── views/videos.py (biblioteca de vídeos)
  ├── views/relatorios.py (análises e CSV)
  ├── services/banco.py (consulta SQLite)
  └── services/video.py (caminhos, horários, miniaturas)
        └── services/config.py (caminhos locais)

Armazenamento: cftv.db (tabela eventos) e diretório videos/ (MP4).
```

## 3. Jornada de uma busca

1. `app.py` chama `carregar_eventos()`, que lê `video, classe, inicio, fim` da tabela `eventos` no SQLite.
2. `app.py` monta as opções de classes e gravações e abre a página selecionada no menu lateral.
3. `views/buscar_eventos.py` recebe filtros informados no formulário.
4. `services/busca.py` retorna eventos que atendem à classe/gravação e que se sobrepõem ao intervalo solicitado.
5. Os resultados ficam em `st.session_state` e o usuário pode selecionar um evento.
6. `components/player.py` monta o player HTML/JavaScript, posicionando-o no início do evento e desenhando marcações com cores por classe.
7. Na branch de streaming, `services/video_stream.py` disponibiliza os bytes do MP4 em `127.0.0.1`, com suporte a requisições HTTP Range.
8. A página de relatórios agrega contagens por classe e vídeo e oferece exportação CSV.

## 4. Decisões técnicas e justificativas a validar

| Decisão | Benefício observável ou esperado | Alternativa e trade-off |
| --- | --- | --- |
| Streamlit | Interface Python rápida, com navegação e componentes prontos | React + API permite maior personalização, mas demanda mais componentes de integração |
| SQLite | Banco em arquivo, sem serviço de banco separado no ambiente local | PostgreSQL facilita maior concorrência e implantação multiusuário, com operação mais complexa |
| Separação em views/services/components | Facilita isolar regras e testar funções de busca | Arquivo único é mais simples inicialmente, mas tende a dificultar manutenção |
| Player HTML/JavaScript | Permite desenhar marcações e legenda personalizadas na timeline | `st.video` é mais simples, mas não fornece o mesmo conjunto de controles personalizados |
| HTTP Range local em vez de Base64 | Evita embutir todo o MP4 no HTML e permite transferir intervalos de bytes | Base64 é simples para vídeos pequenos, mas cresce o documento HTML e o uso de memória |

Essas justificativas ainda precisam ser conectadas aos requisitos formais e, quando relevante, medidas de desempenho.

## 5. Limitações e pendências verificadas

- A branch de streaming ainda precisa ser executada e validada com MP4 reais no ambiente do usuário. Testes automatizados do novo servidor foram adicionados, mas não há resultado de execução relatado.
- O servidor de vídeos está vinculado a `127.0.0.1`, portanto não atende navegadores remotos sem adaptação.
- `views/buscar_eventos.py` envia ao player somente os eventos presentes no resultado filtrado, e não necessariamente todos os eventos do mesmo vídeo.
- O arquivo `views/relatorios.py` usa `use_container_width`, que o Streamlit atual sinaliza para substituição.
- O pipeline que gera detecções (modelo, treinamento, inferência, armazenamento) **não foi confirmado** nos arquivos examinados. Não pressupor que todo esse pipeline esteja implementado no aplicativo.
- Métricas de precisão da detecção, latência, uso de memória e escalabilidade ainda precisam ser coletadas.

## 6. Perguntas para a defesa

**Qual é o papel do `app.py`?** Coordenar inicialização, estado, carregamento de eventos e navegação; delega processamento específico a módulos especializados.

**O que é um evento?** Neste trecho do sistema, é um registro com nome do vídeo, classe detectada, horário inicial e horário final, relativos ao início da gravação.

**Por que SQLite?** É adequado a um protótipo local por simplificar a configuração; a escolha precisa ser reavaliada para concorrência e escala maiores.

**Por que o player não carrega mais Base64?** A nova abordagem reduz o tamanho do HTML e permite que o navegador solicite trechos do MP4 por Range. Ainda é necessária validação com vídeos reais.

**Quais são as limitações?** Execução local do streaming, necessidade de testes de integração, avaliação de desempenho e documentação do pipeline de IA.

## 7. Próxima validação prática

```bash
git fetch origin
git switch melhoria/player-streaming-local
git pull origin melhoria/player-streaming-local
python -m unittest discover -s tests -p "test_*.py" -v
streamlit run app.py
```

Esperamos 27 testes registrados (18 existentes + 9 novos), mas o sucesso da nova bateria depende da execução no ambiente real. Depois, abrir **Buscar eventos**, selecionar uma detecção, verificar início, reprodução, busca na timeline, marcações e legenda.
