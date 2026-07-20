# Contribuindo

Este documento descreve como configurar o ambiente local, instalar as dependências, executar os testes e submeter contribuições para este projeto.

## Visão geral

Este repositório implementa um protocolo experimental para avaliação de métricas de similaridade musical no contexto de detecção de plágio musical. Como o projeto prioriza reprodutibilidade científica, mudanças devem preservar:

* consistência dos pipelines experimentais;
* organização dos artefatos em `data/processed/` e `data/results/`;
* uso controlado de configurações em `config/`;
* separação entre componentes reutilizáveis (`src/preprocessing/`, `src/metrics/`, `src/transformations/`) e pipelines (`src/experiment/`).

## Como configurar o ambiente de trabalho local

### Opção recomendada: Docker

Esta é a forma preferencial de desenvolvimento, pois aproxima o ambiente local do ambiente de execução do experimento.

1. Construa a imagem:

```bash
docker compose build
```

2. Abra um shell no contêiner:

```bash
docker compose run --rm app bash
```

3. Execute os comandos do projeto dentro do contêiner, por exemplo:

```bash
python src/main.py inspect
```

### Opção local com Python

Caso prefira executar sem Docker, utilize um ambiente virtual.

1. Crie o ambiente virtual:

```bash
python -m venv .venv
```

2. Ative o ambiente virtual.

No Linux/macOS:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

3. Atualize o `pip` e instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Dependências do projeto

As dependências principais estão listadas em `requirements.txt` e incluem bibliotecas para:

* processamento simbólico musical;
* manipulação de MIDI;
* análise numérica e tabular;
* geração de gráficos;
* execução de notebooks;
* testes automatizados.

Algumas bibliotecas relevantes:

* `music21`
* `pretty_midi`
* `numpy`
* `pandas`
* `scipy`
* `scikit-learn`
* `matplotlib`
* `seaborn`
* `pyyaml`
* `pytest`

## Como testar as alterações

Antes de submeter uma contribuição, execute pelo menos os testes automatizados relacionados à mudança realizada.

### Executar toda a suíte de testes

```bash
pytest
```

### Executar com cobertura

```bash
pytest --cov=src
```

### Executar um teste específico

```bash
pytest tests/test_smoke_dataset_example.py -q
```

### Smoke test

O projeto possui um smoke test com dataset mínimo de exemplo para validar rapidamente se o fluxo principal está operacional.

```bash
pytest tests/test_smoke_dataset_example.py -q
```

Documentação complementar:

* [tests/smoke/README.md](tests/smoke/README.md)

## Como contribuir

As contribuições podem incluir:

* correções de bugs;
* melhorias em pipelines experimentais;
* refatorações seguras;
* melhorias de documentação;
* ampliação de testes;
* ajustes de reprodutibilidade.

Sempre que possível, mantenha as alterações pequenas, objetivas e fáceis de revisar.

## Fluxo recomendado para submissão

1. Faça um fork do repositório ou crie um branch a partir da branch principal.
2. Implemente a alteração de forma isolada.
3. Execute os testes relevantes.
4. Revise se a mudança não quebrou o protocolo experimental nem a organização dos resultados.
5. Atualize a documentação quando a alteração impactar uso, execução, estrutura ou interpretação dos artefatos.
6. Abra uma pull request com descrição clara da contribuição.

## Pull requests

Ao abrir uma pull request, procure incluir:

* resumo do problema;
* descrição objetiva da solução adotada;
* impacto esperado no experimento ou na arquitetura;
* arquivos principais modificados;
* indicação dos testes executados;
* observações sobre limitações, decisões assumidas ou pontos que merecem revisão.

Se a mudança afetar o protocolo experimental, informe explicitamente:

* qual etapa foi alterada;
* se houve impacto em reprodutibilidade;
* se resultados anteriores precisam ser regenerados.

## Issues

Ao abrir uma issue, procure informar:

* contexto do problema;
* comportamento observado;
* comportamento esperado;
* comandos executados;
* mensagens de erro relevantes;
* sistema operacional e forma de execução utilizada;
* se possível, caminhos dos arquivos de entrada e saída envolvidos.

## Boas práticas para este projeto

Ao contribuir, procure seguir estas diretrizes:

* preservar a responsabilidade única de cada módulo;
* não mover lógica de `src/preprocessing/` para `src/experiment/`;
* não recalcular artefatos desnecessariamente quando o pipeline já possui reaproveitamento;
* manter nomes de código em inglês;
* manter textos voltados ao usuário em português;
* utilizar `pathlib.Path` no código Python quando aplicável;
* evitar alterar dados brutos em `data/raw/`.

## Dados e reprodutibilidade

O diretório `data/raw/` contém ou referencia dados originais do experimento. Esses dados devem ser tratados como imutáveis.

Ao contribuir:

* não modifique datasets brutos manualmente;
* não substitua arquivos de integridade sem justificativa clara;
* documente qualquer mudança que afete artefatos reproduzíveis;
* preserve o uso de seeds e parâmetros em arquivo de configuração quando houver aleatoriedade.

## Dúvidas e contato

Para dúvidas gerais, utilize as issues do repositório. Para contexto adicional sobre o projeto e o experimento, consulte também:

* [README.md](README.md)
* [docs/README.md](docs/README.md)
* [docs/experimental_protocol.md](docs/experimental_protocol.md)
* [docs/reproducibility.md](docs/reproducibility.md)
