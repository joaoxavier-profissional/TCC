# Testes automatizados

Execute na raiz do repositório, no mesmo ambiente Python onde estão instaladas
as dependências do aplicativo (incluindo `streamlit` e `opencv-python`):

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Os testes são independentes do banco SQLite real e dos vídeos do projeto.
Usam registros fictícios e arquivos temporários para cobrir filtros, ordenação,
interseção temporal, conversão de horários e localização de gravações.

**Escopo:** testes de regressão das funções atuais. Não validam o player HTML,
a detecção por IA, nem a interface Streamlit. O formato de minutos/segundos
fora de 00–59 ainda não é validado por `services.video.segundos`; a melhoria
pode ser implementada em outra etapa, com testes próprios.
