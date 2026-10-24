# Interface de upload e processamento

Esta etapa adiciona funções à página **Vídeos** do Streamlit.

## Operações

1. **Adicionar vídeo:** `st.file_uploader` recebe um MP4, grava na pasta local `videos/`, valida se ao menos um frame pode ser lido e mostra o arquivo na biblioteca. Não sobrescreve nomes já existentes. O Streamlit normalmente limita uploads a 200 MB por padrão; o serviço de gravação tem limite adicional de 250 MB. Para arquivos maiores, use a cópia local diretamente na pasta `videos/`.
2. **Testar detecção:** analisa frames amostrados (1 por segundo, nos primeiros 30 segundos), com confiança 10%, incluindo pessoa, bicicleta, carro e motocicleta. Exibe contagem das caixas por classe e **não altera o SQLite**. Não gera imagens anotadas: para investigação detalhada, ainda existe `diagnostico_motos.py`.
3. **Executar indexação completa:** após confirmação, lê todos os frames com YOLO11n e confiança 40%, agrupa detecções e salva os eventos no SQLite. Reindexar substitui somente eventos do vídeo escolhido; os de outros vídeos são preservados. A indexação é síncrona e mantém a página ocupada durante o processamento.

## Executar

```bash
git fetch origin
git switch funcionalidade/upload-processamento-interface
git pull origin funcionalidade/upload-processamento-interface
python -m unittest discover -s tests -p "test_*.py" -v
streamlit run app.py
```

Abra **Vídeos** no menu. Faça backup de `cftv.db` antes de realizar a primeira indexação pela interface. O arquivo `yolo11n.pt` deve existir na raiz; nenhum download automático é feito por esse fluxo.

**Testes automatizados:** foram adicionados cinco testes de upload; não demonstram execução visual do Streamlit nem eficácia da detecção YOLO.

## Para explicar à banca

- Upload é armazenamento de uma gravação; não é indexação.
- Diagnóstico analisa somente amostras e retorna contagem de caixas; não conta objetos únicos, nem mede precisão/recall.
- Indexação processa todos os frames, agrupa classes por intervalo e persiste eventos para pesquisa.
- A interface usa serviços Python separados para que as regras de upload, detecção e armazenamento possam ser testadas e mantidas independentemente.

## Limitações

- O funcionamento foi projetado para Streamlit **local**, em ambiente confiável, sem autenticação. Não publique a aplicação em rede aberta sem controle de acesso, isolamento e proteção adicional.
- Uploads grandes consomem recursos do Streamlit; há limite de tamanho e espaço no disco deve ser monitorado.
- Processamento síncrono pode demorar e não mostra porcentagem de avanço.
- Arquivos maliciosos ou corrompidos exigem medidas adicionais de segurança em uso público.
- O streaming do player personalizado continua limitado a navegadores no mesmo computador do servidor.
