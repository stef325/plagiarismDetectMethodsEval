# Reprodutibilidade

## Objetivo

Este documento descreve os elementos necessários para reproduzir o experimento com o mesmo ambiente, os mesmos parâmetros e a mesma organização de artefatos.

## Artefato público de reprodutibilidade

O projeto também está associado ao seguinte registro público:

* OSF: <https://doi.org/10.17605/OSF.IO/FUAVC>

Esse identificador pode ser usado para referenciar o artefato de reprodução do experimento.

## Ambiente de execução

O projeto utiliza:

* Python;
* Docker;
* Docker Compose v2;
* dependências registradas em `requirements.txt`.

Os artefatos de containerização estão nos arquivos:

* `Dockerfile`
* `docker-compose.yaml`

## Ambiente utilizado nas execuções reportadas

As execuções reportadas no repositório foram realizadas em ambiente conteinerizado com:

* Docker `29.6.1`, verificado em 17 de julho de 2026.

Ambiente hospedeiro:

* sistema operacional hospedeiro: Windows 11;
* processador: 11th Gen Intel(R) Core(TM) i3-1115G4 @ 3.00GHz;
* memória RAM instalada: 32,0 GB;
* placa gráfica: Intel(R) UHD Graphics (128 MB).

Essas informações ajudam a contextualizar o ambiente computacional empregado na reprodução do experimento.

## Dataset

Para reprodução correta, o POP909 deve estar disponível em:

`data/raw/POP909`

A validação de integridade e a origem dos dados estão documentadas em:

* [Datasets](datasets.md)

## Configuração central

Os principais parâmetros do experimento ficam em:

`config/default.yaml`

Entre eles:

* caminho do dataset;
* seeds aleatórias;
* tamanho do subconjunto;
* tamanho dos segmentos;
* quantidade de segmentos por música;
* transformações habilitadas;
* parâmetros das transformações;
* parâmetros das métricas;
* pesos da métrica global;
* limiar de avaliação.

## Execução recomendada

### Construção do ambiente

```bash
docker compose build
```

### Execução completa

```bash
docker compose run --rm app python src/main.py all
```

### Execução com configuração específica

```bash
docker compose run --rm app python src/main.py --config config/default.yaml all
```

## Reprodução via notebook

O projeto também possui notebooks voltados à reprodução e inspeção dos resultados:

* `notebooks/00_full_experiment_colab.ipynb`: notebook principal para execução completa, inclusive em Google Colab;
* `notebooks/01_step_by_step_execution.ipynb`: execução passo a passo das etapas;
* `notebooks/02_results_analysis.ipynb`: inspeção dos resultados já gerados.

O notebook principal foi criado para facilitar a reprodução em ambientes interativos, especialmente quando o objetivo é demonstrar o pipeline completo sem depender apenas da linha de comando.

## Política de reprodução

Para reproduzir os mesmos resultados, é importante manter:

* o mesmo arquivo de configuração;
* as mesmas seeds;
* a mesma versão do dataset;
* a mesma estrutura de diretórios;
* a mesma versão do código.

## Reprodução completa versus reanálise

### Reprodução completa

A reprodução completa envolve reexecutar todas as etapas do pipeline, desde a inspeção do dataset até a consolidação e geração das figuras.

### Reanálise dos resultados

Para outra pessoa reanalisar os resultados sem refazer todo o pipeline, os artefatos mais importantes são:

* resultados de similaridade em CSV ou JSON;
* resultados de robustez;
* resultados de interpretabilidade;
* consolidação final;
* figuras e tabelas derivadas.

## Cuidados importantes

Alguns fatores podem alterar os resultados de uma reexecução:

* mudança de versão de bibliotecas;
* diferenças no processamento MIDI;
* alteração de limiar de similaridade;
* alteração de pesos da métrica global;
* mudança do subconjunto selecionado;
* mudança das seeds.

## Ameaças à reprodutibilidade

Conforme discutido no artigo, a reexecução pode ser afetada por:

* versões de bibliotecas;
* diferenças no tratamento de eventos MIDI;
* caminhos locais presentes em alguns artefatos tabulares;
* variações de configuração entre execuções.

Por isso, é importante preservar:

* identificadores das músicas;
* parâmetros das transformações;
* sementes aleatórias;
* pesos da métrica global;
* versões das ferramentas utilizadas.

## Artefatos produzidos

As saídas do experimento são separadas em:

* `data/processed/`: artefatos intermediários;
* `data/results/experiment/`: resultados de comparação;
* `data/results/evaluation/`: avaliações;
* `data/results/consolidated/`: consolidação final;
* `data/results/figures/`: visualizações.

## Artefatos mínimos recomendados para compartilhamento

Se o objetivo for compartilhar os resultados com outra pessoa ou com uma IA para análise posterior, os arquivos mais importantes são:

* `data/results/experiment/similarity_results.csv`
* `data/results/evaluation/robustness_metrics.csv`
* `data/results/evaluation/interpretability/interpretability_results.csv`
* `data/results/consolidated/consolidated_results.json`
* `data/results/consolidated/consolidated_results.md`

Dependendo do objetivo, também podem ser úteis:

* `data/results/consolidated/experiment_summary.csv`
* `data/results/consolidated/statistics_summary.csv`
* `data/results/figures/visualizations.md`
* diretório `data/results/figures/`

## Documentos relacionados

* [README principal](../README.md)
* [Protocolo experimental](experimental_protocol.md)
* [Guia dos resultados](results_guide.md)
* [Datasets](datasets.md)
