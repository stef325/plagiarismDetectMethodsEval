# Musical Plagiarism Detection Metrics Evaluation

## Sobre o projeto

Este repositório contém o desenvolvimento do experimento proposto no artigo **"Avaliação da Robustez e Interpretabilidade de Métricas de Similaridade Musical para Detecção de Plágio em Músicas Geradas por IA"**.

O objetivo do projeto é investigar como diferentes métricas de similaridade musical se comportam na detecção de similaridade suspeita entre músicas representadas simbolicamente em formato MIDI. O experimento utiliza o dataset **POP909** e avalia métricas melódicas, harmônicas, rítmicas e uma métrica global sob diferentes transformações musicais controladas.

Além da implementação do experimento, este repositório busca garantir **reprodutibilidade**, documentando todas as etapas do desenvolvimento, ambiente de execução e configuração dos experimentos.

---

## Estado atual

Atualmente o projeto encontra-se na fase de configuração da infraestrutura de desenvolvimento.

Até o momento foram concluídas as seguintes atividades:

* Estrutura inicial do projeto
* Configuração do ambiente utilizando Docker
* Organização dos diretórios do projeto
* Definição das dependências Python
* Configuração do versionamento com Git

As etapas relacionadas ao processamento do dataset e implementação das métricas serão desenvolvidas nas próximas fases.

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

## Documentação

A documentação do projeto encontra-se na pasta `docs`.

Os principais documentos são:

* Plano de desenvolvimento
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
