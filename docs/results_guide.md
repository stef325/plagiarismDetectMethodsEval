# Guia dos Resultados

## Objetivo

Este documento resume os principais artefatos gerados pelo experimento e como eles podem ser interpretados.

## Principais diretórios de saída

### `data/processed/`

Contém artefatos intermediários produzidos ao longo do pipeline, como:

* dataset limpo;
* subconjunto selecionado;
* segmentos extraídos;
* representações musicais;
* transformações geradas.

### `data/results/experiment/`

Contém os resultados diretamente ligados às comparações experimentais, incluindo:

* pares experimentais;
* resultados das métricas de similaridade.

### `data/results/evaluation/`

Contém os resultados das avaliações posteriores, como:

* robustez;
* interpretabilidade.

### `data/results/consolidated/`

Contém tabelas e resumos consolidados para análise final.

### `data/results/figures/`

Contém as figuras geradas para inspeção visual e potencial uso no artigo.

## Resumo dos resultados reportados no artigo

O manuscrito atual reporta, entre outros, os seguintes números:

* 909 músicas do POP909 inspecionadas;
* 2.898 arquivos MIDI carregados com sucesso;
* 0 arquivos MIDI classificados como inválidos;
* 200 representações musicais válidas;
* 2.800 pares positivos;
* 2.800 pares negativos;
* 5.600 pares comparados no total.

Esses valores correspondem ao recorte experimental descrito no artigo e devem ser interpretados em conjunto com a configuração usada na execução.

## Como interpretar os resultados

### Pares positivos

Representam comparações entre um segmento original e uma transformação derivada dele.

Em geral, espera-se que apresentem similaridade relativamente mais alta do que pares negativos.

### Pares negativos

Representam comparações entre segmentos não relacionados.

Em geral, espera-se que apresentem similaridade mais baixa.

### Robustez

A avaliação de robustez observa o desempenho das métricas ao classificar pares como positivos ou negativos, usando medidas como:

* precisão;
* revocação;
* F1-score;
* taxa de falsos negativos.

Também é analisada a **queda de similaridade**, que mede quanto a transformação reduz o escore em relação à comparação de referência.

### Interpretabilidade

A avaliação de interpretabilidade observa se a variação dos escores acompanha o componente musical realmente transformado.

Exemplos esperados:

* transformações melódicas impactam mais as métricas melódicas;
* transformações harmônicas impactam mais as métricas harmônicas;
* transformações rítmicas impactam mais as métricas rítmicas.

## Principais achados reportados

De acordo com o artigo:

* os pares negativos apresentaram score global médio muito baixo, indicando boa rejeição de trechos sem relação conhecida;
* o limiar de 0,70 gerou alta precisão, mas baixa revocação;
* as transformações rítmicas causaram a maior queda média de similaridade;
* métricas de melodia e harmonia obtiveram melhor equilíbrio entre precisão e revocação do que várias métricas rítmicas;
* os scores separados por componente foram mais interpretáveis do que a métrica global isolada.

## Limitações de interpretação

Os resultados devem ser lidos com algumas restrições:

* o estudo trabalha com similaridade suspeita, não com decisão jurídica de plágio;
* a análise utiliza MIDI, e não áudio final;
* o experimento usa transformações controladas, e não saídas reais de modelos generativos;
* o comportamento das métricas depende do limiar adotado e da parametrização do experimento.

## Documentos relacionados

* [Protocolo experimental](experimental_protocol.md)
* [Reprodutibilidade](reproducibility.md)
* [Arquitetura do projeto](architecture.md)
* [Visão geral do projeto](project_overview.md)
