# Arquitetura do Projeto

## Princípios gerais

A arquitetura do projeto foi organizada para separar claramente:

* ponto de entrada da aplicação;
* pipelines experimentais;
* componentes reutilizáveis de pré-processamento;
* transformações musicais;
* métricas de similaridade;
* validações e consolidação de resultados.

## Organização principal

### `src/main.py`

Responsável por:

* expor os comandos de execução;
* carregar o arquivo de configuração;
* acionar os pipelines do experimento.

### `src/experiment/`

Contém os pipelines do protocolo experimental. Cada módulo nessa pasta representa uma etapa ou atividade do experimento.

Exemplos:

* inspeção;
* validação do dataset;
* extração de segmentos;
* transformações;
* métricas;
* avaliações;
* consolidação;
* visualizações.

### `src/preprocessing/`

Contém componentes reutilizáveis voltados ao pré-processamento, sem incorporar responsabilidades específicas do protocolo experimental.

Exemplos:

* inspeção estrutural do dataset;
* carregamento de arquivos MIDI;
* extração de representações musicais.

### `src/transformations/`

Contém as transformações musicais controladas, organizadas por componente:

* melodia;
* harmonia;
* ritmo;
* combinações.

### `src/metrics/`

Agrupa as métricas de similaridade por família:

* métricas melódicas;
* métricas harmônicas;
* métricas rítmicas;
* métricas globais.

### `tests/`

Contém os testes automatizados do projeto.

## Fluxo entre os módulos

Em termos gerais:

1. `experiment/` orquestra a execução;
2. `preprocessing/` fornece os insumos reutilizáveis;
3. `transformations/` altera representações musicais;
4. `metrics/` calcula similaridades;
5. novos pipelines em `experiment/` avaliam, consolidam e visualizam os resultados.

## Documentos relacionados

* [Visão geral do projeto](project_overview.md)
* [Protocolo experimental](experimental_protocol.md)
* [Reprodutibilidade](reproducibility.md)
