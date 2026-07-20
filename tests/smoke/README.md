# Smoke Test

Esta documentação reúne os smoke tests disponíveis no projeto.

Atualmente, existem dois tipos de smoke test:

* um smoke test funcional, com dataset mínimo de exemplo e saída esperada;
* um smoke test estrutural, que valida a ordem do fluxo principal `all`.

## Objetivo

Permitir que qualquer pessoa verifique em poucos minutos se o fluxo mínimo do projeto está íntegro.

## Smoke test funcional

### O que é validado

O smoke test funcional usa um dataset mínimo do POP909 com apenas uma música e valida:

* inspeção da estrutura do dataset;
* limpeza do dataset;
* validação do carregamento dos arquivos MIDI.

### Como executar

```bash
pytest tests/test_smoke_dataset_example.py -q
```

### Arquivos principais

* `example_dataset/`: estrutura mínima de entrada;
* `expected_output.csv`: saída esperada do smoke test.
* `tests/test_smoke_dataset_example.py`: teste que executa o fluxo mínimo real e compara a saída obtida com a saída esperada.

## Smoke test estrutural

### O que é validado

O smoke test estrutural verifica se o comando principal `all` continua executando as etapas do experimento na ordem documentada no protocolo.

Esse teste:

* não executa o experimento real;
* substitui as etapas por funções leves;
* registra a sequência de chamadas;
* compara a ordem observada com a ordem esperada.

### Como executar

```bash
pytest tests/test_smoke_main.py -q
```

### Arquivo principal

* `tests/test_smoke_main.py`: teste de fumaça estrutural do fluxo principal do projeto.
