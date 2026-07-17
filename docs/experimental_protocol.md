# Protocolo Experimental

## Visão geral

O experimento foi organizado em etapas independentes, porém encadeadas, para permitir execução modular e reprodutível.

Ele constitui uma avaliação **quantitativa, comparativa e controlada** de métricas de similaridade musical aplicadas à análise de similaridade suspeita entre trechos do POP909.

## Estrutura conceitual do experimento

O experimento parte de um trecho MIDI de referência e cria cenários de comparação em três grupos:

* cópia direta;
* versão transformada;
* trecho não relacionado.

Esses cenários permitem avaliar se as métricas conseguem preservar similaridade nos casos relacionados e rejeitar semelhanças espúrias nos casos não relacionados.

## Variáveis do experimento

### Variáveis independentes

As principais variáveis controladas são:

* tipo de versão candidata;
* componente musical transformado;
* tipo de transformação aplicada;
* métrica de similaridade utilizada.

### Variáveis dependentes

Os principais resultados observados são:

* escores de similaridade por componente;
* escore global;
* queda de similaridade em relação à cópia direta;
* precisão;
* revocação;
* F1-score;
* taxa de falsos negativos;
* coerência interpretativa entre transformação e escores.

## Pares experimentais

### Pares positivos

Um par positivo contém:

* um segmento original;
* uma versão transformada derivada desse mesmo segmento.

Esses pares representam o cenário em que há relação conhecida entre as duas instâncias comparadas.

### Pares negativos

Um par negativo contém:

* um segmento original;
* um trecho de outra música ou de outro segmento sem relação conhecida.

Esses pares representam o cenário em que não se espera similaridade relevante.

## Representações musicais

Cada segmento é decomposto em três componentes:

* melodia;
* harmonia;
* ritmo.

Essas representações são a base para as transformações e para o cálculo das métricas.

## Transformações musicais controladas

O protocolo aplica transformações em quatro grupos:

* transformações melódicas;
* transformações harmônicas;
* transformações rítmicas;
* transformações combinadas.

### Transformações melódicas

Incluem, entre outras:

* transposição;
* simplificação melódica;
* ornamentação;
* alteração de intervalos.

### Transformações harmônicas

Incluem, entre outras:

* substituição de acordes;
* reharmonização;
* simplificação harmônica.

### Transformações rítmicas

Incluem, entre outras:

* mudança de andamento;
* alteração proporcional das durações;
* modificação rítmica parcial.

## Métricas avaliadas

### Métricas melódicas

* n-gramas intervalares;
* maior subsequência comum;
* distância de edição melódica.

### Métricas harmônicas

* n-gramas de acordes;
* distância de edição harmônica;
* similaridade por classes de altura.

### Métricas rítmicas

* n-gramas rítmicos;
* similaridade IOI;
* distância de edição rítmica.

### Métrica global

* média simples;
* média ponderada entre os componentes melódico, harmônico e rítmico.

## Critérios de avaliação

A avaliação é dividida em dois eixos:

### Robustez

Observa se a métrica:

* mantém escores relativamente altos para pares positivos;
* mantém escores baixos para pares negativos.

Os indicadores quantitativos usados incluem:

* precisão;
* revocação;
* F1-score;
* taxa de falsos negativos;
* queda de similaridade por transformação.

### Interpretabilidade

Observa se o comportamento dos escores acompanha o componente musical efetivamente transformado.

Exemplos:

* quando apenas a harmonia é alterada, espera-se maior impacto nas métricas harmônicas;
* quando apenas o ritmo é alterado, espera-se maior impacto nas métricas rítmicas;
* quando a transformação é combinada, espera-se redução coerente nos componentes alterados.

## Etapas do protocolo

### 1. Inspeção e validação do dataset

Nesta etapa, o projeto:

* verifica se a estrutura do POP909 está correta;
* valida a presença dos arquivos esperados;
* testa o carregamento dos arquivos MIDI principais.

### 2. Preparação dos dados

Após a validação inicial, o experimento:

* separa os arquivos principais do dataset;
* seleciona um subconjunto reproduzível;
* extrai segmentos em compassos;
* registra metadados dos segmentos.

### 3. Extração de representações musicais

Cada segmento é transformado em representações específicas:

* melodia;
* harmonia;
* ritmo.

### 4. Aplicação das transformações

As transformações controladas são aplicadas para simular versões candidatas derivadas dos trechos de referência.

### 5. Formação dos pares

Os pares positivos e negativos são construídos para avaliação discriminativa das métricas.

### 6. Cálculo das métricas

O projeto calcula:

* métricas melódicas;
* métricas harmônicas;
* métricas rítmicas;
* métrica global.

### 7. Avaliação experimental

Os resultados das métricas são usados para avaliar:

* robustez;
* interpretabilidade;
* comportamento global do conjunto de métricas.

### 8. Consolidação e visualização

Ao final, o experimento:

* consolida tabelas e estatísticas;
* gera relatórios;
* produz figuras para análise e uso no artigo.

## Comandos relacionados

Os comandos operacionais estão descritos no [README principal](../README.md) e a lógica de reprodução está em [Reprodutibilidade](reproducibility.md).

## Documentos relacionados

* [Visão geral do projeto](project_overview.md)
* [Guia dos resultados](results_guide.md)
* [Plano de desenvolvimento](development_plan.md)
