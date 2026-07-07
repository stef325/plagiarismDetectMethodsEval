# Musical Plagiarism Detection Metrics Evaluation

## Sobre o projeto

Este repositório contém o desenvolvimento do experimento proposto no artigo **"Avaliação da Robustez e Interpretabilidade de Métricas de Similaridade Musical para Detecção de Plágio em Músicas Geradas por IA"**.

O objetivo do projeto é investigar como diferentes métricas de similaridade musical se comportam na detecção de similaridade suspeita entre músicas representadas simbolicamente em formato MIDI. O experimento utiliza o dataset **POP909** e avalia métricas melódicas, harmônicas, rítmicas e uma métrica global sob diferentes transformações musicais controladas.

Além da implementação do experimento, este repositório busca garantir **reprodutibilidade**, documentando todas as etapas do desenvolvimento, ambiente de execução e configuração dos experimentos.

---

## Estado atual

Até o momento, o projeto já possui:

* Estrutura de diretórios do repositório.
* Ambiente Docker para execução reproduzível.
* Configuração central em YAML.
* Documentação do dataset POP909 em `docs/datasets.md`.
* `DatasetInspector` para inspecionar a estrutura do dataset.
* `POP909Loader` para carregar arquivos MIDI com `pretty_midi`.
* Pipeline de inspeção do dataset.
* Pipeline de limpeza do dataset, que copia apenas os MIDI principais para `data/processed/POP909`.
* Pipeline de validação dos arquivos MIDI.
* Interface de linha de comando com `argparse` para executar cada etapa do experimento.
* Testes unitários para os componentes e pipelines já criados.

---

## Tecnologias utilizadas

* Python
* Docker
* Git
* GitHub

Bibliotecas Python atualmente utilizadas:

* music21
* pretty_midi
* numpy
* pandas
* scipy
* scikit-learn
* matplotlib
* jupyter
* notebook
* pyyaml
* tqdm

---
## Estrutura atual do experimento

As etapas disponíveis no `src/experiment/` são:

* `inspect_dataset`: inspeciona a estrutura do dataset bruto.
* `clean_dataset`: prepara a área processada com apenas os MIDI principais.
* `validate_dataset`: valida se os arquivos MIDI podem ser carregados.

O arquivo `src/main.py` funciona como ponto de entrada da aplicação e expõe comandos para executar cada etapa separadamente ou o fluxo completo.

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
├── LICENSE
├── requirements.txt
└── README.md
```

---

## Como validar o ambiente

### Construir a imagem Docker

```bash
docker build -t music-plagiarism .
```

### Executar o container

Linux/macOS

```bash
docker run -it -v $(pwd):/app music-plagiarism
```

Windows PowerShell

```powershell
docker run -it -v ${PWD}:/app music-plagiarism
```

Após iniciar o container, execute:

```bash
python --version
```

e verifique se todas as dependências estão instaladas corretamente:

```bash
pip list
```
---
## Executar o experimento
### Como executar com Docker

Construir a imagem:

```bash
docker compose build
```

Executar todo o experimento:

```bash
docker compose run --rm app python src/main.py all
```

Executar uma etapa específica:

```bash
docker compose run --rm app python src/main.py inspect
docker compose run --rm app python src/main.py clean
docker compose run --rm app python src/main.py validate
```

#### Saídas geradas

* Relatório da inspeção em `data/results/inspect_dataset/`.
* Dataset limpo em `data/processed/POP909/`.
* Relatório da validação em `data/results/validate_dataset/`.

---

## Documentação

A documentação do projeto encontra-se na pasta `docs`.

Os principais documentos são:

* [Plano de desenvolvimento](docs/development_plan.md)
* [Datasets e validação de integridade](docs/datasets.md)
* Arquitetura do projeto *(em breve)*
* Protocolo experimental *(em breve)*
* Documentação do ambiente *(em breve)*

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
