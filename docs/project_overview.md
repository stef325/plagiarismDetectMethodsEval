# Visão Geral do Projeto

## Contexto

A detecção de plágio musical depende fortemente de como a similaridade entre duas músicas é representada e medida. Em cenários com músicas geradas ou transformadas por sistemas de IA, essa análise se torna ainda mais sensível, pois pequenas mudanças estruturais podem alterar o comportamento das métricas de forma não trivial.

Este projeto investiga esse problema em nível experimental, utilizando representações simbólicas em formato MIDI e um conjunto controlado de transformações musicais.

## Problema de pesquisa

O problema central do trabalho é entender se métricas de similaridade musical conseguem:

* distinguir pares realmente relacionados de pares não relacionados;
* reagir de forma coerente ao componente musical alterado;
* manter comportamento interpretável quando submetidas a transformações controladas.

## Perguntas de pesquisa

As perguntas de pesquisa formalizadas no artigo são:

* `RQ1`: métricas de similaridade musical conseguem detectar possível plágio em versões transformadas de trechos do POP909 após alterações em melodia, harmonia e ritmo?
* `RQ2`: quais componentes musicais, quando transformados, reduzem a robustez das métricas de similaridade?
* `RQ3`: métricas separadas por componente musical tornam a análise de similaridade mais interpretável do que métricas globais?

## Hipóteses

O estudo foi conduzido com base nas seguintes hipóteses:

* `H1`: transformações melódicas causam maior queda na detecção de similaridade suspeita do que transformações harmônicas ou rítmicas.
* `H2`: métricas específicas por componente musical são mais interpretáveis do que métricas globais, pois permitem identificar a origem musical da similaridade.
* `H3`: uma abordagem combinada, agregando similaridade melódica, harmônica e rítmica, é mais robusta para detectar possível plágio do que métricas isoladas.

## Objetivo geral

Avaliar a robustez e a interpretabilidade de métricas de similaridade musical para apoio à detecção de plágio musical.

## Objetivos específicos

* avaliar métricas melódicas, harmônicas, rítmicas e globais;
* aplicar transformações controladas sobre representações musicais;
* medir o impacto dessas transformações nos escores de similaridade;
* comparar o comportamento das métricas em pares positivos e negativos;
* consolidar resultados para análise experimental.

## Contribuições do trabalho

As principais contribuições previstas no artigo são:

* definição de um desenho experimental controlado para comparar trechos de referência do POP909 e versões candidatas transformadas;
* organização de métricas melódicas, harmônicas, rítmicas e globais para avaliação de similaridade musical;
* análise conjunta de robustez e interpretabilidade como critérios de apoio à detecção computacional de similaridade suspeita.

## Escopo

O projeto:

* utiliza o dataset POP909;
* trabalha com músicas em formato MIDI;
* opera sobre representações musicais derivadas dos segmentos;
* avalia métricas já implementadas no repositório;
* não implementa um sistema final de decisão jurídica ou pericial sobre plágio;
* não utiliza músicas geradas por IA como dados experimentais.

## Delimitações importantes

Neste trabalho:

* a similaridade é tratada como indicador computacional de possível plágio, e não como decisão jurídica;
* a IA generativa aparece como contexto de aplicação e motivação do problema;
* as versões candidatas são produzidas por transformações controladas, e não por modelos generativos;
* a análise é realizada sobre representações simbólicas MIDI, não sobre áudio final.

## Documentos relacionados

* [Protocolo experimental](experimental_protocol.md)
* [Reprodutibilidade](reproducibility.md)
* [Arquitetura do projeto](architecture.md)
* [Datasets](datasets.md)
* [Guia dos resultados](results_guide.md)
