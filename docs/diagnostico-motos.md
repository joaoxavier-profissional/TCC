# Diagnóstico de motocicletas — YOLO11n

**Propósito:** investigar por que motocicletas visíveis em `videoplayback.mp4` não aparecem entre os eventos indexados.

Este diagnóstico não modifica `cftv.db`, `indexar_video.py` nem a configuração de produção (confiança de 0,40). Examina frames amostrados em vez de todos os frames e executa o modelo com confiança mínima de 0,10, sem filtro de classes, para investigar classes confundidas (principalmente bicicleta, classe COCO 1, e motocicleta, classe COCO 3).

## Executar

Com `venv` ativado e `yolo11n.pt` já presente:

```bash
git fetch origin
git switch diagnostico/motocicletas-yolo
git pull origin diagnostico/motocicletas-yolo
python -m unittest discover -s tests -p "test_*.py" -v
python diagnostico_motos.py videoplayback.mp4 --inicio 0 --duracao 120 --passo 1
```

**Para investigar um trecho específico:** `--inicio 90 --duracao 30 --passo 0.5`. Por padrão, amostra aproximadamente um frame por segundo nos primeiros 120 segundos. Pode não observar motocicletas que só aparecem em instantes entre as amostras.

## Saídas

Em `diagnosticos/videoplayback/` (ignorado pelo Git):

- `deteccoes_diagnostico.csv`: tempo, classe, identificador COCO e confiança de cada caixa detectada;
- até oito imagens anotadas para frames em que detectou bicicleta ou motocicleta;
- resumo no terminal para limiares 0,10, 0,20, 0,30 e 0,40.

As contagens representam **caixas detectadas em frames amostrados**, não motos únicas e nem precisão/recall; o mesmo objeto pode aparecer em diversos frames.

## Interpretação

- Moto identificada com confiança 0,10–0,39 mas não 0,40: o filtro de confiança pode estar removendo algumas detecções.
- Muitas detecções como bicicleta: possível confusão de classe a investigar nas imagens.
- Nenhuma moto ou bicicleta: verificar o trecho analisado, tamanho das motos, iluminação, oclusões e limitações do modelo.
- Uma moto visível sem caixa anotada pode representar um falso negativo; para calcular recall formalmente é necessário anotar a verdade de referência.

**Não reduza a confiança na indexação sem avaliar falsos positivos.** Após observar os resultados, podemos decidir se vale ajustar o limite, aumentar resolução, usar outro modelo ou selecionar frames com mais cuidado.
