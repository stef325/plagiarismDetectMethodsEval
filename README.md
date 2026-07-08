# Musical Plagiarism Detection Metrics Evaluation

## Sobre o projeto

Este repositório contém o desenvolvimento do experimento proposto no artigo **"Avaliação da Robustez e Interpretabilidade de Métricas de Similaridade Musical para Detecção de Plágio em Músicas Geradas por IA"**.

O objetivo do projeto é investigar como diferentes métricas de similaridade musical se comportam na detecção de similaridade suspeita entre músicas representadas simbolicamente em formato MIDI. O experimento utiliza o dataset **POP909** e avalia métricas melódicas, harmônicas, rítmicas e uma métrica global sob diferentes transformações musicais controladas.

Além da implementação do experimento, este repositório busca garantir **reprodutibilidade**, documentando etapas, ambiente de execução e parâmetros utilizados.

---

## Estado atual

Até o momento, o projeto já possui:

* Estrutura de diretórios do repositório.
* Ambiente Docker para execução reproduzível.
* Configuração central em YAML.
* Documentação do dataset POP909 em `docs/datasets.md`.
* `POP909Inspector` para inspecionar a estrutura do dataset.
* `POP909Loader` para carregar arquivos MIDI com `pretty_midi`.
* Pipelines do protocolo experimental, da inspeção do dataset até a consolidação e visualização dos resultados.
* Interface de linha de comando com `argparse` para executar cada etapa do experimento.
* Testes unitários para os componentes e pipelines implementados.

---

## Tecnologias utilizadas

* Python
* Docker
* Git
* GitHub

Bibliotecas Python utilizadas:

* music21
* pretty_midi
* numpy
* pandas
* scipy
* scikit-learn
* matplotlib
* seaborn
* jupyter
* notebook
* pyyaml
* tqdm

---

## Estrutura atual do experimento

O arquivo `src/main.py` funciona como ponto de entrada da aplicação e expõe comandos para executar cada etapa separadamente ou o fluxo completo.

Comandos atualmente disponíveis:

* `inspect`: inspeciona a estrutura do dataset bruto.
* `clean`: copia apenas os MIDI principais para a área processada.
* `validate`: valida se os arquivos MIDI do dataset podem ser carregados.
* `subset`: seleciona um subconjunto reproduzível do dataset processado.
* `segments`: extrai segmentos aleatórios em compassos.
* `representations`: extrai representações melódicas, harmônicas e rítmicas.
* `melody_transform`: aplica transformações melódicas.
* `harmony_transform`: aplica transformações harmônicas.
* `rhythm_transform`: aplica transformações rítmicas.
* `combined_transform`: aplica transformações combinadas.
* `validate_representations`: valida as representações extraídas.
* `validate_transformations`: valida as transformações geradas.
* `compute_melody_metrics`: calcula as métricas de similaridade melódica.
* `compute_harmony_metrics`: calcula as métricas de similaridade harmônica.
* `compute_rhythm_metrics`: calcula as métricas de similaridade rítmica.
* `compute_global_metrics`: calcula a métrica global.
* `validate_metrics`: executa a validação automatizada das métricas.
* `build_experiment_pairs`: forma os pares experimentais positivos e negativos.
* `run_experiment`: executa as métricas sobre os pares experimentais.
* `evaluate_robustness`: avalia a robustez das métricas.
* `evaluate_interpretability`: avalia a interpretabilidade das métricas.
* `consolidate_results`: consolida os resultados produzidos.
* `generate_visualizations`: gera as figuras do experimento.
* `all`: executa o fluxo completo em sequência.

---

## Estrutura do projeto

```text
.
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── docs/
├── notebooks/
├── src/
│   ├── experiment/
│   ├── metrics/
│   ├── preprocessing/
│   ├── transformations/
│   └── main.py
├── tests/
├── Dockerfile
├── docker-compose.yaml
├── LICENSE
├── requirements.txt
└── README.md
```

---

## Como executar

### Pré-requisitos

* Docker e Docker Compose v2.
* Dataset POP909 extraído em `data/raw/POP909`.
* Arquivos de integridade do dataset conforme descrito em `docs/datasets.md`.

### Execução recomendada com Docker Compose

Construir a imagem:

```bash
docker compose build
```

Listar a ajuda do programa:

```bash
docker compose run --rm app python src/main.py --help
```

Executar o experimento completo:

```bash
docker compose run --rm app python src/main.py all
```

Executar uma etapa específica:

```bash
docker compose run --rm app python src/main.py inspect
docker compose run --rm app python src/main.py clean
docker compose run --rm app python src/main.py validate
docker compose run --rm app python src/main.py subset
docker compose run --rm app python src/main.py segments
docker compose run --rm app python src/main.py representations
docker compose run --rm app python src/main.py melody_transform
docker compose run --rm app python src/main.py harmony_transform
docker compose run --rm app python src/main.py rhythm_transform
docker compose run --rm app python src/main.py combined_transform
docker compose run --rm app python src/main.py validate_representations
docker compose run --rm app python src/main.py validate_transformations
docker compose run --rm app python src/main.py compute_melody_metrics
docker compose run --rm app python src/main.py compute_harmony_metrics
docker compose run --rm app python src/main.py compute_rhythm_metrics
docker compose run --rm app python src/main.py compute_global_metrics
docker compose run --rm app python src/main.py validate_metrics
docker compose run --rm app python src/main.py build_experiment_pairs
docker compose run --rm app python src/main.py run_experiment
docker compose run --rm app python src/main.py evaluate_robustness
docker compose run --rm app python src/main.py evaluate_interpretability
docker compose run --rm app python src/main.py consolidate_results
docker compose run --rm app python src/main.py generate_visualizations
```

### Execução com arquivo de configuração alternativo

O projeto utiliza `config/default.yaml` por padrão. Para usar outro arquivo:

```bash
docker compose run --rm app python src/main.py --config config/default.yaml inspect
```

Exemplo com o fluxo completo:

```bash
docker compose run --rm app python src/main.py --config config/default.yaml all
```

### Execução local sem Docker

Também é possível executar localmente, desde que as dependências de `requirements.txt` estejam instaladas:

```bash
python src/main.py inspect
python src/main.py all
```

### Fluxo sugerido do protocolo experimental

Para executar o experimento passo a passo, a ordem recomendada é:

1. `inspect`
2. `clean`
3. `validate`
4. `subset`
5. `segments`
6. `representations`
7. `melody_transform`
8. `harmony_transform`
9. `rhythm_transform`
10. `combined_transform`
11. `validate_representations`
12. `validate_transformations`
13. `compute_melody_metrics`
14. `compute_harmony_metrics`
15. `compute_rhythm_metrics`
16. `compute_global_metrics`
17. `validate_metrics`
18. `build_experiment_pairs`
19. `run_experiment`
20. `evaluate_robustness`
21. `evaluate_interpretability`
22. `consolidate_results`
23. `generate_visualizations`

### Principais saídas geradas

* Inspeção do dataset: `data/results/inspect_dataset/`
* Limpeza do dataset: `data/processed/POP909/`
* Validação dos arquivos MIDI: `data/results/validate_dataset/`
* Subconjunto processado: `data/processed/subset/`
* Segmentos extraídos: `data/processed/segments/`
* Representações extraídas: `data/processed/representations/`
* Transformações: `data/processed/transformations/`
* Pares experimentais: `data/results/experiment/pairs/`
* Similaridades do experimento: `data/results/experiment/`
* Avaliações: `data/results/evaluation/`
* Consolidação: `data/results/consolidated/`
* Figuras: `data/results/figures/`

---

## Configuração do experimento

Os principais parâmetros do experimento ficam em `config/default.yaml`, incluindo:

* caminho do dataset;
* seed aleatória;
* tamanho do subconjunto;
* quantidade de compassos por segmento;
* quantidade de segmentos por música;
* transformações habilitadas;
* parâmetros das transformações;
* parâmetros das métricas;
* pesos da métrica global;
* limiar de avaliação.

---

## Documentação

A documentação do projeto encontra-se na pasta `docs`.

Os principais documentos são:

* [Plano de desenvolvimento](docs/development_plan.md)
* [Datasets e validação de integridade](docs/datasets.md)

---

## Plano de desenvolvimento

O desenvolvimento do projeto está organizado em etapas independentes.

O acompanhamento das tarefas pode ser encontrado em:

```text
docs/development_plan.md
```

Cada etapa implementada corresponde a uma funcionalidade documentada e versionada no repositório.

---

## Licença

Projeto desenvolvido para fins de pesquisa acadêmica.
