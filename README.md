# Musical Plagiarism Detection Metrics Evaluation

## Descrição do projeto

Este repositório reúne a implementação experimental do artigo **"Avaliação da Robustez e Interpretabilidade de Métricas de Similaridade Musical para Detecção de Plágio Musical"**.

O projeto investiga como métricas de similaridade musical se comportam ao comparar músicas em formato simbólico MIDI, com foco especial em:

* robustez a transformações musicais controladas;
* interpretabilidade dos escores produzidos;
* comparação entre métricas melódicas, harmônicas, rítmicas e globais.

O dataset utilizado é o **POP909**, e toda a estrutura do projeto foi organizada para favorecer **reprodutibilidade científica**.

---

## Objetivo do experimento

O objetivo do experimento é avaliar se diferentes métricas de similaridade:

* distinguem adequadamente pares positivos e negativos;
* respondem de forma coerente ao componente musical transformado;
* mantêm comportamento interpretável sob diferentes manipulações musicais.

Este estudo trata os resultados como **indicadores computacionais de similaridade suspeita**, e não como determinação jurídica ou pericial de plágio.

---

## Perguntas de pesquisa

O experimento é orientado pelas seguintes perguntas:

* `RQ1`: métricas de similaridade musical conseguem detectar possível plágio em versões transformadas de trechos do POP909 após alterações em melodia, harmonia e ritmo?
* `RQ2`: quais componentes musicais, quando transformados, reduzem a robustez das métricas de similaridade?
* `RQ3`: métricas separadas por componente musical tornam a análise de similaridade mais interpretável do que métricas globais?

---

## Hipóteses

As hipóteses avaliadas no artigo são:

* `H1`: transformações melódicas causam maior queda na detecção de similaridade suspeita do que transformações harmônicas ou rítmicas.
* `H2`: métricas específicas por componente musical são mais interpretáveis do que métricas globais.
* `H3`: uma abordagem combinada, agregando similaridade melódica, harmônica e rítmica, é mais robusta para detectar possível plágio do que métricas isoladas.

---

## Escopo e delimitações

Este repositório documenta um experimento controlado com as seguintes características:

* utiliza o POP909 como dataset principal;
* trabalha com representações simbólicas em MIDI;
* avalia pares positivos e negativos formados a partir de trechos musicais;
* utiliza transformações controladas em melodia, harmonia, ritmo e combinações;
* não utiliza músicas geradas por IA como dados experimentais;
* não tem como objetivo emitir decisão jurídica sobre plágio.

A geração musical por IA aparece no trabalho como **contexto de aplicação e motivação do problema**, mas o experimento em si usa versões transformadas controladamente a partir do POP909.

---

## Visão geral do experimento

O protocolo experimental segue, em alto nível, o fluxo abaixo:

1. inspecionar e validar o dataset;
2. preparar uma versão processada com os arquivos principais;
3. selecionar um subconjunto reproduzível;
4. extrair segmentos musicais;
5. gerar representações melódicas, harmônicas e rítmicas;
6. aplicar transformações musicais controladas;
7. formar pares experimentais positivos e negativos;
8. calcular métricas de similaridade;
9. avaliar robustez e interpretabilidade;
10. consolidar resultados e gerar visualizações.

### Pares experimentais

* par positivo: trecho original comparado com uma versão transformada derivada do mesmo segmento;
* par negativo: trecho original comparado com outro trecho sem relação conhecida.

---

## Métricas e critérios de avaliação

As famílias de métricas avaliadas são:

* melódicas: n-gramas intervalares, maior subsequência comum e distância de edição melódica;
* harmônicas: n-gramas de acordes, distância de edição harmônica e similaridade por classes de altura;
* rítmicas: n-gramas rítmicos, similaridade IOI e distância de edição rítmica;
* globais: média simples e média ponderada entre os componentes.

Os principais critérios de avaliação utilizados são:

* precisão;
* revocação;
* F1-score;
* taxa de falsos negativos;
* queda de similaridade;
* interpretabilidade por componente musical.

---

## Principais resultados

De acordo com os resultados consolidados no artigo:

* 909 músicas do POP909 foram inspecionadas;
* 2.898 arquivos MIDI foram carregados com sucesso;
* 200 representações musicais válidas foram consideradas na análise;
* 5.600 pares foram comparados, sendo 2.800 positivos e 2.800 negativos;
* as métricas apresentaram alta precisão para rejeitar pares negativos;
* a revocação foi baixa sob o limiar adotado, indicando sensibilidade limitada para parte dos pares positivos transformados;
* as transformações rítmicas produziram a maior queda média de similaridade;
* os escores por componente mostraram-se mais interpretáveis do que a métrica global isolada.

Esses resultados sugerem que as métricas são promissoras para triagem computacional de similaridade suspeita, mas ainda exigem calibração e análise conjunta por componente.

---

## Documentação complementar

Para conhecer melhor o artigo, o desenho experimental e os artefatos de reprodução antes da execução, a documentação detalhada foi organizada em arquivos específicos:

* [Sumário da documentação](docs/README.md)
* [Visão geral do projeto](docs/project_overview.md)
* Smoke test: [tests/smoke/README.md](tests/smoke/README.md)
* [Protocolo experimental](docs/experimental_protocol.md)
* [Reprodutibilidade](docs/reproducibility.md)
* [Arquitetura do projeto](docs/architecture.md)
* [Datasets](docs/datasets.md)
* [Guia dos resultados](docs/results_guide.md)
* [Plano de desenvolvimento](docs/development_plan.md)

---

## Links importantes

* Projeto no OSF: <https://doi.org/10.17605/OSF.IO/FUAVC>
* Sumário da documentação: [docs/README.md](docs/README.md)
* Documentação do dataset POP909: [docs/datasets.md](docs/datasets.md)
* Protocolo experimental: [docs/experimental_protocol.md](docs/experimental_protocol.md)
* Documentação do smoke test: [tests/smoke/README.md](tests/smoke/README.md)
* Reprodutibilidade: [docs/reproducibility.md](docs/reproducibility.md)
* Guia dos resultados: [docs/results_guide.md](docs/results_guide.md)


---

## Como instalar as dependências

### Opção recomendada com Docker

Construir a imagem:

```bash
docker compose build
```

Essa é a forma recomendada para manter o ambiente alinhado ao experimento.

### Instalação local com Python

Pré-requisitos:

* Python compatível com o projeto;
* `pip` disponível no ambiente.

Instalação:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

As principais bibliotecas utilizadas incluem:

* `music21`
* `pretty_midi`
* `numpy`
* `pandas`
* `scipy`
* `scikit-learn`
* `matplotlib`
* `seaborn`
* `pyyaml`
* `tqdm`

---

## Como executar a análise

### Pré-requisitos de dados

Antes da execução, é necessário:

* disponibilizar o dataset POP909 em `data/raw/POP909`;
* manter os arquivos de integridade do dataset conforme descrito em `docs/datasets.md`.

### Smoke test

Se quiser uma verificação rápida antes da execução completa, o projeto possui um smoke test com dataset mínimo de exemplo e saída esperada.

```bash
pytest tests/test_smoke_dataset_example.py -q
```

Detalhes do smoke test:

* [tests/smoke/README.md](tests/smoke/README.md)

### Execução completa

Com Docker:

```bash
docker compose run --rm app python src/main.py all
```

Sem Docker:

```bash
python src/main.py all
```

### Execução alternativa com notebooks

Se preferir, o usuário também pode executar o experimento por meio dos notebooks do projeto, em vez de usar apenas a linha de comando.

Ordem recomendada dos notebooks:

1. `24_full_experiment_colab.ipynb`: notebook principal para execução completa, inclusive em Google Colab.
2. `25_step_by_step_execution.ipynb`: notebook para execução por etapas.
3. `26_results_analysis.ipynb`: notebook para inspeção dos resultados já produzidos.

### Ordem dos scripts

Se a análise for executada passo a passo, a ordem recomendada é:

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

### Exemplos de execução por etapa

```bash
docker compose run --rm app python src/main.py inspect
docker compose run --rm app python src/main.py validate
docker compose run --rm app python src/main.py run_experiment
docker compose run --rm app python src/main.py consolidate_results
```

### Executar com outro arquivo de configuração

O projeto utiliza `config/default.yaml` por padrão. Para usar outro arquivo:

```bash
docker compose run --rm app python src/main.py --config config/default.yaml all
```

---

## O que cada pasta e arquivo principal faz

### Pastas principais

* `config/`: arquivos de configuração do experimento, incluindo seeds, parâmetros e caminhos.
* `data/raw/`: dados brutos originais do projeto, incluindo o dataset POP909.
* `data/processed/`: artefatos intermediários gerados ao longo do pré-processamento e das transformações.
* `data/results/`: resultados finais e relatórios do experimento.
* `docs/`: documentação detalhada do projeto, protocolo, arquitetura e reprodutibilidade.
* `notebooks/`: espaço para execução interativa do experimento, reprodução em notebook e análises complementares.
* `src/`: código-fonte principal do projeto.
* `src/experiment/`: pipelines que implementam cada etapa do protocolo experimental.
* `src/preprocessing/`: componentes reutilizáveis de pré-processamento e carregamento de dados.
* `src/transformations/`: transformações musicais controladas.
* `src/metrics/`: métricas de similaridade musical.
* `tests/`: testes automatizados do projeto.
* `notebooks/24_full_experiment_colab.ipynb`: notebook principal obrigatório para reprodução completa, inclusive em ambiente Google Colab.
* `notebooks/25_step_by_step_execution.ipynb`: notebook para execução passo a passo das etapas do experimento.
* `notebooks/26_results_analysis.ipynb`: notebook para inspeção dos resultados já gerados.

### Arquivos principais

* `src/main.py`: ponto de entrada da aplicação e interface de linha de comando.
* `config/default.yaml`: configuração padrão do experimento.
* `requirements.txt`: dependências Python do projeto.
* `Dockerfile`: definição da imagem do ambiente.
* `docker-compose.yaml`: configuração do serviço principal para execução reproduzível.
* `README.md`: visão geral do projeto e instruções principais de uso.
* `pytest.ini`: configuração da suíte de testes.
* `LICENSE`: informações de licenciamento do repositório.

---

## Estrutura principal do repositório

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
├── requirements.txt
└── README.md
```

---

## Ordem dos notebooks

Os notebooks também seguem uma ordem explícita para apoiar a reprodução e a análise:

1. `00_full_experiment_colab.ipynb`: execução completa do experimento em ambiente interativo, com foco em Google Colab.
2. `01_step_by_step_execution.ipynb`: execução modular por etapas, útil para depuração, repetição parcial e acompanhamento do pipeline.
3. `02_results_analysis.ipynb`: leitura e inspeção dos artefatos finais já gerados.

---

## Principais saídas geradas

* inspeção do dataset: `data/results/inspect_dataset/`
* dataset processado: `data/processed/POP909/`
* representações extraídas: `data/processed/representations/`
* transformações: `data/processed/transformations/`
* pares experimentais: `data/results/experiment/pairs/`
* resultados de similaridade: `data/results/experiment/`
* avaliações: `data/results/evaluation/`
* consolidação: `data/results/consolidated/`
* figuras: `data/results/figures/`

---

## Contato

**Autora:** Bruna Stefany da Silva Reinaldo  
**E-mail:** `brunastefany.academico@gmail.com`  
**Instituição:** Universidade Federal de Campina Grande  
**Local:** Campina Grande, Paraíba, Brasil

Para dúvidas, sugestões ou relato de problemas, também é possível utilizar as *issues* deste repositório.

---

## Como citar

Se você utilizar este repositório ou os resultados dele, prefira citar o artigo correspondente.

Referência conforme o manuscrito atual:

```text
Bruna Stefany da Silva Reinaldo. 2026. Avaliação da Robustez e Interpretabilidade de Métricas de Similaridade Musical para Detecção de Plágio Musical. In Proceedings of Reprodutibilidade em Pesquisa em Ciência da Computação (RPCC '26). RPCC, Campina Grande, PB, BR, 10 pages. https://doi.org/10.17605/OSF.IO/FUAVC
```

Como artefato de reprodutibilidade, o projeto também pode ser referenciado pelo DOI do OSF:

```text
Reinaldo, Bruna Stefany da Silva. 2026. Musical Plagiarism Detection Metrics Evaluation. OSF. https://doi.org/10.17605/OSF.IO/FUAVC
```

---

## Ambiente utilizado

As execuções do experimento foram realizadas em ambiente conteinerizado com:

* Docker `29.6.1` (`docker --version` em 17 de julho de 2026);

Ambiente hospedeiro utilizado na execução do Docker:

* sistema operacional hospedeiro: Windows 11;
* processador: 11th Gen Intel(R) Core(TM) i3-1115G4 @ 3.00GHz;
* memória RAM instalada: 32,0 GB;
* placa gráfica: Intel(R) UHD Graphics (128 MB).

Essas informações ajudam a contextualizar o ambiente computacional empregado na reprodução do experimento.

---

## Declaração de utilização de IA

Em conformidade com a Portaria CNPq nº 2.664/2026, declara-se que ferramentas de Inteligência Artificial generativa foram utilizadas como apoio ao desenvolvimento deste trabalho. O *Prism*, com os modelos 5.5 e 5.6-SOL, foi utilizado para apoio à escrita, à organização do trabalho e ao gerenciamento das fontes. O *NotebookLM*, com o modelo Gemini 3.5, foi utilizado para apoio à organização das fontes, incluindo consultas e perguntas sobre os materiais bibliográficos analisados. O *Codex*, nos modelos 5.4 e 5.4-mini, foi utilizado para apoio à criação, estruturação e documentação do código do experimento. O *ChatGPT* na versão Go, com o modelo GPT-5.2 Instant, foi utilizado para apoio à organização do experimento.

O uso dessas ferramentas teve caráter auxiliar. A autora revisou criticamente o conteúdo, as decisões metodológicas, as referências, o código e a versão final do artigo, assumindo responsabilidade integral pela seleção, interpretação e apresentação das informações.

---

## Licença

Este projeto está licenciado sob a licença MIT.

Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
